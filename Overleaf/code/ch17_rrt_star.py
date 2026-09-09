"""Optimal sampling-based planning for chapter 17.

RRT* with Near / ChooseParent / Rewire and cost propagation to the
descendants of a rewired vertex, Informed RRT* with direct sampling of
the prolate hyperspheroid, the k-nearest variant, plain RRT for
comparison, and a fine-grid A* reference for the optimal cost.  The world,
the map of the worked example and the 3D scene are copied from
chapter 16 (code/ch16_rrt.py) so that both chapters plan on the same maps.
NumPy only, ASCII only.

    python3 ch17_rrt_star.py       runs the self-test (well under a minute)

Conventions
-----------
* A configuration x is a NumPy array of length d (d = 2 or 3); the
  planning space X is the box [lower, upper]; X_free is the part of X
  further than `radius` from every obstacle.
* Segments are checked by subdivision as in chapter 16: points spaced at
  most `delta` apart, tested against the boxes inflated by
  radius + delta/2.
* The cost of a path is its Euclidean length.
* Nearest and Near are vectorised linear scans; a kd-tree would make them
  O(log n) but the trees of this chapter have a few thousand vertices.
"""
import heapq
import math
import time

import numpy as np

INF = float("inf")


# ----------------------------------------------------------------------
# The world (from chapter 16)
# ----------------------------------------------------------------------
class World:
    """Box-shaped planning space with box and sphere obstacles."""

    def __init__(self, lower, upper, boxes=(), spheres=(), radius=0.0,
                 delta=0.05):
        self.lower = np.asarray(lower, dtype=float)
        self.upper = np.asarray(upper, dtype=float)
        self.dim = len(self.lower)
        self.box_lo = np.array([b[0] for b in boxes],
                               dtype=float).reshape(-1, self.dim)
        self.box_hi = np.array([b[1] for b in boxes],
                               dtype=float).reshape(-1, self.dim)
        self.sph_c = np.array([s[0] for s in spheres],
                              dtype=float).reshape(-1, self.dim)
        self.sph_r = np.array([s[1] for s in spheres], dtype=float)
        self.radius = float(radius)
        self.delta = float(delta)
        self.segment_checks = 0

    def volume(self):
        """mu(X): the volume of the bounding box."""
        return float(np.prod(self.upper - self.lower))

    def sample(self, rng):
        """A configuration drawn uniformly from X (free or not)."""
        return self.lower + rng.random(self.dim) * (self.upper - self.lower)

    def inside(self, x):
        return bool(np.all(x >= self.lower) and np.all(x <= self.upper))

    def box_distances(self, pts):
        p = pts[:, None, :]
        gap = np.maximum(np.maximum(self.box_lo[None] - p,
                                    p - self.box_hi[None]), 0.0)
        return np.sqrt((gap ** 2).sum(axis=2))

    def points_free(self, pts, margin=None, spheres=True):
        """Is each point inside X and further than `margin` (default: the
        robot radius) from every obstacle?"""
        pts = np.atleast_2d(np.asarray(pts, dtype=float))
        margin = self.radius if margin is None else margin
        ok = np.all((pts >= self.lower) & (pts <= self.upper), axis=1)
        if len(self.box_lo):
            ok &= np.all(self.box_distances(pts) > margin, axis=1)
        if spheres and len(self.sph_c):
            d = np.linalg.norm(pts[:, None, :] - self.sph_c[None], axis=2)
            ok &= np.all(d > self.sph_r + margin, axis=1)
        return ok

    def point_free(self, x):
        return bool(self.points_free(x)[0])

    def segment_free(self, a, b):
        """CollisionFree(a, b) by subdivision (chapter 16)."""
        self.segment_checks += 1
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        n = max(1, int(math.ceil(np.linalg.norm(b - a) / self.delta)))
        pts = a + np.linspace(0.0, 1.0, n + 1)[:, None] * (b - a)
        if not np.all(self.points_free(pts, self.radius + 0.5 * self.delta,
                                       spheres=False)):
            return False
        if len(self.sph_c):
            ab = b - a
            t = (self.sph_c - a) @ ab / max(float(ab @ ab), 1e-300)
            closest = a + np.clip(t, 0.0, 1.0)[:, None] * ab
            d = np.linalg.norm(self.sph_c - closest, axis=1)
            if np.any(d <= self.sph_r + self.radius):
                return False
        return True


def worked_example_world():
    """The 2D map of the worked example of chapters 16 and 17: two walls."""
    return World([0, 0], [10, 10],
                 boxes=[([3, 0], [5, 6]), ([6, 4], [8, 10])],
                 radius=0.0, delta=0.05)


def wide_example_world():
    """The same two walls, start and goal in a 30 x 30 field: the free
    space is nine times larger, so the informed set is a small part of
    it (used for the convergence experiment)."""
    return World([-10, -10], [20, 20],
                 boxes=[([3, 0], [5, 6]), ([6, 4], [8, 10])],
                 radius=0.0, delta=0.05)


def scene_3d():
    """The 3D box field of chapter 16."""
    boxes = [([2, 0, 0], [3, 10, 6]), ([5, 3, 0], [6, 7, 10]),
             ([7, 0, 4], [8, 10, 5]), ([4, 7, 0], [9, 9, 3]),
             ([0, 4, 7], [4, 6, 8]), ([8, 2, 6], [10, 4, 10])]
    return World([0, 0, 0], [10, 10, 10], boxes=boxes, radius=0.3, delta=0.1)


def tiny_world():
    """The ten-vertex hand example of the text (Near, ChooseParent, Rewire)."""
    return World([0, 0], [6, 4.5], boxes=[([2.6, 1.9], [3.1, 2.45])],
                 radius=0.0, delta=0.05)


# ----------------------------------------------------------------------
# Small helpers (from chapter 16 where marked)
# ----------------------------------------------------------------------
def steer(x_near, x_rand, eta):
    """Move from x_near towards x_rand by at most eta (chapter 16)."""
    d = x_rand - x_near
    dist = np.linalg.norm(d)
    if dist <= eta:
        return x_rand.copy()
    return x_near + (eta / dist) * d


def random_in_ball(rng, d, r=1.0):
    """A point drawn uniformly from the ball of radius r in R^d."""
    u = rng.normal(size=d)
    u /= np.linalg.norm(u)
    return u * r * rng.random() ** (1.0 / d)


def path_length(path):
    path = np.asarray(path, dtype=float)
    return float(np.linalg.norm(np.diff(path, axis=0), axis=1).sum())


def path_is_free(world, path, factor=10):
    """Check a path with a `factor` times finer subdivision (chapter 16)."""
    fine = World(world.lower, world.upper,
                 boxes=list(zip(world.box_lo, world.box_hi)),
                 spheres=list(zip(world.sph_c, world.sph_r)),
                 radius=world.radius, delta=world.delta / factor)
    return all(fine.segment_free(path[k], path[k + 1])
               for k in range(len(path) - 1))


def prune(path, world):
    """Greedy string pulling (chapter 16): jump to the furthest later
    vertex that a free straight segment can reach."""
    path = np.asarray(path, dtype=float)
    out, i = [path[0]], 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not world.segment_free(path[i], path[j]):
            j -= 1
        out.append(path[j])
        i = j
    return np.array(out)


def visibility_shortest_path(world, start, goal, offset=0.005):
    """Exact optimum among 2D boxes (chapter 16): Dijkstra on the
    visibility graph of the box corners pushed outward by the inflation of
    the collision checker plus `offset`."""
    off = world.radius + 0.5 * world.delta + offset
    pts = [np.asarray(start, dtype=float), np.asarray(goal, dtype=float)]
    for lo, hi in zip(world.box_lo, world.box_hi):
        for x in (lo[0] - off, hi[0] + off):
            for y in (lo[1] - off, hi[1] + off):
                c = np.array([x, y])
                if np.all(c > world.lower) and np.all(c < world.upper) \
                        and world.point_free(c):
                    pts.append(c)
    n = len(pts)
    dist = np.full(n, INF)
    prev = np.full(n, -1, dtype=int)
    done = np.zeros(n, dtype=bool)
    dist[0] = 0.0
    for _ in range(n):
        cand = np.where(done, INF, dist)
        i = int(np.argmin(cand))
        if not np.isfinite(cand[i]) or i == 1:
            break
        done[i] = True
        for j in range(n):
            if not done[j]:
                dij = np.linalg.norm(pts[j] - pts[i])
                if dist[i] + dij < dist[j] and \
                        world.segment_free(pts[i], pts[j]):
                    dist[j], prev[j] = dist[i] + dij, i
    if not np.isfinite(dist[1]):
        return None, INF
    idx, i = [], 1
    while i >= 0:
        idx.append(i)
        i = prev[i]
    return np.array([pts[k] for k in idx[::-1]]), float(dist[1])


def unit_ball_volume(d):
    """zeta_d: the volume of the unit ball in R^d (pi in 2D, 4pi/3 in 3D)."""
    return math.pi ** (d / 2.0) / math.gamma(d / 2.0 + 1.0)


def gamma_star(d, mu_free):
    """The threshold 2 (1 + 1/d)^(1/d) (mu(X_free) / zeta_d)^(1/d) of
    Karaman and Frazzoli; gamma must exceed it."""
    return 2.0 * (1.0 + 1.0 / d) ** (1.0 / d) * \
        (mu_free / unit_ball_volume(d)) ** (1.0 / d)


def free_volume(world, n=200000, seed=0):
    """Monte Carlo estimate of mu(X_free)."""
    rng = np.random.default_rng(seed)
    pts = world.lower + rng.random((n, world.dim)) * (world.upper - world.lower)
    return world.volume() * float(world.points_free(pts).mean())


def connection_radius(n, d, gamma, eta):
    """r_n = min(gamma (log n / n)^(1/d), eta) with n = |V|."""
    n = max(int(n), 2)
    return min(gamma * (math.log(n) / n) ** (1.0 / d), eta)


def knn_count(n, d, k_rrg=None):
    """k_n = ceil(k_RRG log n) with k_RRG > e (1 + 1/d)."""
    if k_rrg is None:
        k_rrg = 1.1 * math.e * (1.0 + 1.0 / d)
    return int(math.ceil(k_rrg * math.log(max(int(n), 2))))


# ----------------------------------------------------------------------
# The tree with costs, children lists and cost propagation
# ----------------------------------------------------------------------
class StarTree:
    """Vertices, parents, edge lengths, costs-to-come and children lists.

    cost[i] is always cost[parent[i]] + edge[i]; set_parent() keeps this
    invariant by propagating the new cost to every descendant."""

    def __init__(self, root, capacity=1024):
        root = np.asarray(root, dtype=float)
        cap = max(int(capacity), 8)
        self.V = np.zeros((cap, len(root)))
        self.parent = np.full(cap, -1, dtype=int)
        self.edge = np.zeros(cap)
        self.cost = np.zeros(cap)
        self.children = [[] for _ in range(cap)]
        self.V[0] = root
        self.n = 1

    def _grow(self):
        cap = len(self.V)
        self.V = np.vstack([self.V, np.zeros_like(self.V)])
        self.parent = np.concatenate([self.parent, np.full(cap, -1, dtype=int)])
        self.edge = np.concatenate([self.edge, np.zeros(cap)])
        self.cost = np.concatenate([self.cost, np.zeros(cap)])
        self.children += [[] for _ in range(cap)]

    def add(self, x, parent, edge_len):
        if self.n == len(self.V):
            self._grow()
        i = self.n
        self.V[i], self.parent[i], self.edge[i] = x, parent, edge_len
        self.cost[i] = self.cost[parent] + edge_len
        self.children[parent].append(i)
        self.n += 1
        return i

    def nearest(self, x):
        d2 = ((self.V[:self.n] - x) ** 2).sum(axis=1)
        return int(np.argmin(d2))

    def near(self, x, r):
        """Indices of all vertices within distance r of x (Near)."""
        d2 = ((self.V[:self.n] - x) ** 2).sum(axis=1)
        return np.flatnonzero(d2 <= r * r)

    def knearest(self, x, k):
        """Indices of the k vertices closest to x (k-nearest variant)."""
        d2 = ((self.V[:self.n] - x) ** 2).sum(axis=1)
        if k >= self.n:
            return np.arange(self.n)
        return np.argpartition(d2, k - 1)[:k]

    def set_parent(self, i, p, edge_len):
        """Rewire vertex i under p and update the costs of its subtree."""
        self.children[self.parent[i]].remove(i)
        self.parent[i], self.edge[i] = p, edge_len
        self.children[p].append(i)
        stack = [i]
        while stack:
            v = stack.pop()
            self.cost[v] = self.cost[self.parent[v]] + self.edge[v]
            stack.extend(self.children[v])

    def path_to(self, i):
        idx = []
        while i >= 0:
            idx.append(i)
            i = self.parent[i]
        return self.V[idx[::-1]].copy()

    def edges(self):
        return [(int(self.parent[i]), i) for i in range(1, self.n)]

    def costs_consistent(self):
        """True if cost[i] == cost[parent[i]] + |V[i] - V[parent[i]]|."""
        for i in range(1, self.n):
            p = self.parent[i]
            if abs(self.cost[i] - self.cost[p]
                   - np.linalg.norm(self.V[i] - self.V[p])) > 1e-9:
                return False
        return True


# ----------------------------------------------------------------------
# Informed sampling: the prolate hyperspheroid
# ----------------------------------------------------------------------
def rotation_to_world_frame(a1):
    """Rotation matrix C with C e_1 = a1 (Gammell et al. 2014): from the
    SVD U S V^T of a1 e_1^T take C = U diag(1, ..., 1, det U det V) V^T."""
    d = len(a1)
    M = np.outer(a1, np.eye(d)[0])
    U, _, Vt = np.linalg.svd(M)
    D = np.ones(d)
    D[-1] = np.linalg.det(U) * np.linalg.det(Vt)
    return U @ np.diag(D) @ Vt


class InformedSampler:
    """Uniform samples from the set of points whose distance to x_start
    plus distance to x_goal is at most c_best: a prolate hyperspheroid
    with transverse diameter c_best and conjugate diameter
    sqrt(c_best^2 - c_min^2), intersected with the box X."""

    def __init__(self, start, goal):
        self.start = np.asarray(start, dtype=float)
        self.goal = np.asarray(goal, dtype=float)
        self.d = len(self.start)
        self.centre = 0.5 * (self.start + self.goal)
        self.c_min = float(np.linalg.norm(self.goal - self.start))
        self.C = rotation_to_world_frame((self.goal - self.start) / self.c_min)
        self.draws = 0            # candidate points drawn
        self.rejections = 0       # candidates outside the target set

    def semi_axes(self, c_best):
        r1 = 0.5 * c_best
        r2 = 0.5 * math.sqrt(max(c_best ** 2 - self.c_min ** 2, 0.0))
        return np.array([r1] + [r2] * (self.d - 1))

    def measure(self, c_best):
        """Volume of the hyperspheroid: zeta_d times the product of axes."""
        return unit_ball_volume(self.d) * float(np.prod(self.semi_axes(c_best)))

    def contains(self, x, c_best):
        return (np.linalg.norm(x - self.start) + np.linalg.norm(x - self.goal)
                <= c_best + 1e-9)

    def sample(self, rng, c_best, world):
        """One sample uniform on (hyperspheroid intersect X)."""
        if not np.isfinite(c_best):
            return world.sample(rng)
        if self.measure(c_best) > world.volume():
            while True:                       # the box is the smaller set
                self.draws += 1
                x = world.sample(rng)
                if self.contains(x, c_best):
                    return x
                self.rejections += 1
        L = np.diag(self.semi_axes(c_best))
        while True:                           # the spheroid is smaller
            self.draws += 1
            x_ball = random_in_ball(rng, self.d)
            x = self.C @ (L @ x_ball) + self.centre
            if world.inside(x):
                return x
            self.rejections += 1


# ----------------------------------------------------------------------
# RRT*, Informed RRT*, k-nearest RRT* and plain RRT
# ----------------------------------------------------------------------
class Result:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def rrt_star(world, start, goal, eta=1.0, gamma=None, p_goal=0.05,
             max_iters=3000, seed=0, informed=False, knn=False, k_rrg=None,
             choose_parent=True, rewire=True, snapshots=()):
    """RRT* (Karaman and Frazzoli 2011).  The goal point itself is sampled
    with probability p_goal until it becomes a vertex; from then on the
    tree path to the goal vertex is the current best path and its cost
    c_best is non-increasing.  informed=True samples the hyperspheroid once
    c_best is finite (Informed RRT*, Gammell et al. 2014); knn=True uses
    the k-nearest variant; choose_parent=rewire=False gives plain RRT.

    Returns a Result with .path, .cost, .tree, .goal_index,
    .solution_iter, .history (rows: iteration, |V|, r_n or k_n, c_best),
    .snapshots {iteration: (|V|, path or None)}, .near_sizes (mean size of
    the Near set) and .segment_checks."""
    rng = np.random.default_rng(seed)
    start = np.asarray(start, dtype=float)
    goal = np.asarray(goal, dtype=float)
    d = world.dim
    if gamma is None:
        gamma = 1.1 * gamma_star(d, world.volume())
    tree = StarTree(start, max_iters + 2)
    sampler = InformedSampler(start, goal)
    goal_index, solution_iter, c_best = -1, None, INF
    history = np.zeros((max_iters, 4))
    snaps, near_total, checks0 = {}, 0, world.segment_checks
    for it in range(1, max_iters + 1):
        # --- Sample ------------------------------------------------------
        if goal_index < 0 and rng.random() < p_goal:
            x_rand = goal
        elif informed:
            x_rand = sampler.sample(rng, c_best, world)
        else:
            x_rand = world.sample(rng)
        # --- Nearest, Steer, CollisionFree (as in RRT) -------------------
        i_nearest = tree.nearest(x_rand)
        x_new = steer(tree.V[i_nearest], x_rand, eta)
        d_nearest = float(np.linalg.norm(x_new - tree.V[i_nearest]))
        radius = (knn_count(tree.n, d, k_rrg) if knn
                  else connection_radius(tree.n, d, gamma, eta))
        if d_nearest > 1e-12 and world.segment_free(tree.V[i_nearest], x_new):
            # --- Near ----------------------------------------------------
            if knn:
                near = tree.knearest(x_new, radius)
            else:
                near = tree.near(x_new, radius)
            near_total += len(near)
            dists = np.linalg.norm(tree.V[near] - x_new, axis=1)
            # --- ChooseParent (c_par is local; c_min is the ------------
            #     start-goal distance of the informed set) ------------------
            i_par, c_par = i_nearest, tree.cost[i_nearest] + d_nearest
            if choose_parent and len(near):
                cand = tree.cost[near] + dists
                for k in np.argsort(cand):           # cheapest first
                    if cand[k] >= c_par:
                        break
                    if world.segment_free(tree.V[near[k]], x_new):
                        i_par, c_par = int(near[k]), float(cand[k])
                        break
            i_new = tree.add(x_new, i_par, c_par - tree.cost[i_par])
            # --- Rewire --------------------------------------------------
            if rewire:
                for k in range(len(near)):
                    j = int(near[k])
                    if j == i_par:
                        continue
                    via = c_par + dists[k]
                    if via < tree.cost[j] - 1e-12 and \
                            world.segment_free(x_new, tree.V[j]):
                        tree.set_parent(j, i_new, dists[k])
            if goal_index < 0 and np.linalg.norm(x_new - goal) < 1e-9:
                goal_index, solution_iter = i_new, it
        if goal_index >= 0:
            c_best = float(tree.cost[goal_index])
        history[it - 1] = (it, tree.n, radius, c_best)
        if it in snapshots:      # |V|, best path and parents at this time
            snaps[it] = (tree.n, tree.path_to(goal_index)
                         if goal_index >= 0 else None,
                         tree.parent[:tree.n].copy())
    path = tree.path_to(goal_index) if goal_index >= 0 else None
    return Result(path=path, cost=c_best, tree=tree, goal_index=goal_index,
                  solution_iter=solution_iter, history=history,
                  snapshots=snaps, near_sizes=near_total / max_iters,
                  segment_checks=world.segment_checks - checks0,
                  gamma=gamma, sampler=sampler)


def rrt_plain(world, start, goal, **kw):
    """RRT with the same sampling and goal handling, no ChooseParent and
    no Rewire: the first path found is never improved."""
    return rrt_star(world, start, goal, choose_parent=False, rewire=False,
                    **kw)


# ----------------------------------------------------------------------
# Reference optimum: A* on a fine grid, then string pulling
# ----------------------------------------------------------------------
def grid_astar_reference(world, start, goal, h=0.1):
    """Shortest path on the 8-connected (2D) or 26-connected (3D) grid of
    spacing h, no corner cutting, followed by greedy string pulling with
    the same collision checker as the planners.  Returns
    (pruned path, its length, length of the raw grid path)."""
    d = world.dim
    shape = tuple(int(round((world.upper[k] - world.lower[k]) / h)) + 1
                  for k in range(d))
    idx = np.indices(shape).reshape(d, -1).T
    pts = world.lower + h * idx
    free = world.points_free(pts).reshape(shape)
    moves = [m for m in np.indices((3,) * d).reshape(d, -1).T - 1
             if np.any(m != 0)]
    s = tuple(int(round(v)) for v in (start - world.lower) / h)
    g = tuple(int(round(v)) for v in (goal - world.lower) / h)
    assert free[s] and free[g], "start or goal is not a free grid point"

    def heur(c):
        return h * math.sqrt(sum((c[k] - g[k]) ** 2 for k in range(d)))

    dist = {s: 0.0}
    prev = {}
    heap = [(heur(s), s)]
    closed = set()
    while heap:
        f, c = heapq.heappop(heap)
        if c in closed:
            continue
        closed.add(c)
        if c == g:
            break
        for m in moves:
            nb = tuple(c[k] + int(m[k]) for k in range(d))
            if any(nb[k] < 0 or nb[k] >= shape[k] for k in range(d)):
                continue
            if not free[nb]:
                continue
            # no corner cutting: every axis-aligned neighbour on the way
            # of a diagonal move must be free as well
            ok = True
            for k in range(d):
                if m[k] != 0:
                    side = list(c)
                    side[k] += int(m[k])
                    if not free[tuple(side)]:
                        ok = False
            if not ok:
                continue
            nd = dist[c] + h * math.sqrt(float(np.sum(m ** 2)))
            if nd < dist.get(nb, INF):
                dist[nb] = nd
                prev[nb] = c
                heapq.heappush(heap, (nd + heur(nb), nb))
    if g not in dist:
        return None, INF, INF
    cells, c = [], g
    while c != s:
        cells.append(c)
        c = prev[c]
    cells.append(s)
    grid_path = world.lower + h * np.array(cells[::-1], dtype=float)
    taut = prune(grid_path, world)
    return taut, path_length(taut), dist[g]


# ----------------------------------------------------------------------
# The hand example of the text (figures of Near, ChooseParent, Rewire)
# ----------------------------------------------------------------------
TINY_VERTICES = [(0.5, 0.5), (1.6, 0.2), (2.8, 0.2), (4.0, 0.2), (4.5, 1.3),
                 (0.9, 1.7), (2.1, 2.4), (3.3, 3.1), (4.4, 3.0), (5.2, 3.8)]
TINY_PARENTS = [-1, 0, 1, 2, 3, 0, 5, 6, 4, 8]


def tiny_example(x_rand=(4.0, 2.1), eta=1.0, r=2.0):
    """One RRT* iteration on the ten-vertex tree of the text.  Returns a
    dictionary with every intermediate quantity (used by the figures, the
    worked trace and exercise 1)."""
    world = tiny_world()
    tree = StarTree(TINY_VERTICES[0], 16)
    for i in range(1, len(TINY_VERTICES)):
        p = TINY_PARENTS[i]
        x = np.array(TINY_VERTICES[i])
        tree.add(x, p, float(np.linalg.norm(x - tree.V[p])))
    cost_before = tree.cost[:tree.n].copy()
    x_rand = np.array(x_rand, dtype=float)
    i_nearest = tree.nearest(x_rand)
    x_new = steer(tree.V[i_nearest], x_rand, eta)
    near = tree.near(x_new, r)
    dists = np.linalg.norm(tree.V[near] - x_new, axis=1)
    cand = tree.cost[near] + dists
    free = [world.segment_free(tree.V[j], x_new) for j in near]
    order = np.argsort(cand)
    i_par = None
    for k in order:
        if free[k]:
            i_par = int(near[k])
            c_par = float(cand[k])
            break
    i_new = tree.add(x_new, i_par, c_par - tree.cost[i_par])
    rewired = []
    for k in range(len(near)):
        j = int(near[k])
        if j == i_par:
            continue
        via = c_par + dists[k]
        if via < tree.cost[j] and world.segment_free(x_new, tree.V[j]):
            old_parent = int(tree.parent[j])
            tree.set_parent(j, i_new, dists[k])
            rewired.append((j, old_parent))
    return dict(world=world, tree=tree, x_rand=x_rand, x_new=x_new,
                nearest=i_nearest, near=[int(j) for j in near],
                candidates=dict((int(near[k]), (float(cand[k]), bool(free[k])))
                                for k in range(len(near))),
                parent=i_par, cost_new=c_par, rewired=rewired,
                cost_before=cost_before, cost_after=tree.cost[:tree.n].copy(),
                new_index=i_new)


# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------
def _self_test():
    t0 = time.time()
    rng = np.random.default_rng(0)

    # 1. the constants ----------------------------------------------------
    assert abs(unit_ball_volume(2) - math.pi) < 1e-12
    assert abs(unit_ball_volume(3) - 4 * math.pi / 3) < 1e-12
    g2 = gamma_star(2, 76.0)
    assert abs(g2 - 2 * math.sqrt(1.5) * math.sqrt(76 / math.pi)) < 1e-9
    assert connection_radius(3000, 2, 13.3, 1.0) < 1.0 < \
        connection_radius(200, 2, 13.3, 5.0)
    print("gamma* for the worked example (mu = 76): %.3f" % g2)

    # 2. the hand example -------------------------------------------------
    ex = tiny_example()
    assert ex["nearest"] == 4 and sorted(ex["near"]) == [3, 4, 6, 7, 8]
    assert ex["parent"] == 7 and not ex["candidates"][6][1]
    assert ex["rewired"] == [(8, 4)]
    assert ex["tree"].costs_consistent()
    assert ex["cost_after"][9] < ex["cost_before"][9]      # propagated
    print("hand example: nearest v%d, near %s, parent v%d, cost %.3f, "
          "rewired %s; v8 %.3f -> %.3f, v9 %.3f -> %.3f" % (
              ex["nearest"], ex["near"], ex["parent"], ex["cost_new"],
              ex["rewired"], ex["cost_before"][8], ex["cost_after"][8],
              ex["cost_before"][9], ex["cost_after"][9]))
    for j, (c, ok) in sorted(ex["candidates"].items(), key=lambda t: t[1][0]):
        print("   candidate v%d: cost via it %.3f, segment free: %s" % (j, c, ok))

    # 3. informed sampling ------------------------------------------------
    for d in (2, 3):
        s = rng.random(d) * 3
        g = s + rng.random(d) * 4 + 1
        samp = InformedSampler(s, g)
        e1 = np.eye(d)[0]
        assert np.allclose(samp.C @ e1, (g - s) / samp.c_min)
        assert np.allclose(samp.C @ samp.C.T, np.eye(d))
        assert abs(np.linalg.det(samp.C) - 1) < 1e-9
        world = World(np.full(d, -20.0), np.full(d, 20.0))
        for c_best in (1.05 * samp.c_min, 1.5 * samp.c_min, 3 * samp.c_min):
            pts = np.array([samp.sample(rng, c_best, world) for _ in range(500)])
            dsum = (np.linalg.norm(pts - s, axis=1)
                    + np.linalg.norm(pts - g, axis=1))
            assert np.all(dsum <= c_best + 1e-9)
            assert np.max(dsum) > 0.97 * c_best        # reaches the boundary
        # the box-is-smaller branch
        small = World(np.full(d, -1.0), np.full(d, 1.0))
        x = samp.sample(rng, 5 * samp.c_min, small)
        assert small.inside(x) and samp.contains(x, 5 * samp.c_min)
    print("informed samples lie in the hyperspheroid (2D and 3D)")

    # 4. the worked example: RRT* on the map of chapter 16 ----------------
    world = worked_example_world()
    start, goal = np.array([1.0, 1.0]), np.array([9.0, 9.0])
    ref_path, ref_len, grid_len = grid_astar_reference(world, start, goal, 0.1)
    assert path_is_free(world, ref_path)
    vis_path, vis_len = visibility_shortest_path(world, start, goal)
    assert path_is_free(world, vis_path) and vis_len <= ref_len
    assert 16.7 < vis_len < 17.0          # corner-to-corner path + clearance
    mu_free = free_volume(world)
    assert abs(mu_free - 76.0) < 1.0
    gamma = 13.3
    assert gamma > gamma_star(2, 76.0)
    res = rrt_star(world, start, goal, eta=1.0, gamma=gamma, p_goal=0.05,
                   max_iters=3000, seed=1, snapshots=(200, 1000, 3000))
    assert res.path is not None and path_is_free(world, res.path)
    assert np.allclose(res.path[0], start) and np.allclose(res.path[-1], goal)
    assert abs(path_length(res.path) - res.cost) < 1e-9
    assert res.tree.costs_consistent()
    c = res.history[:, 3]
    finite = np.isfinite(c)
    assert finite[-1] and np.all(np.diff(c[finite]) <= 1e-12)   # monotone
    assert res.cost <= 1.05 * ref_len and res.cost <= 1.05 * vis_len
    assert res.cost >= vis_len - 1e-6     # nothing beats the optimum
    print("worked example (seed 1): first solution at iteration %d with "
          "cost %.3f; after 3000 iterations %d vertices, cost %.3f; "
          "optimum %.3f (visibility graph), grid A* %.3f (taut %.3f); "
          "mean |Near| %.1f; %d segment checks" % (
              res.solution_iter, c[finite][0], res.tree.n, res.cost,
              vis_len, grid_len, ref_len, res.near_sizes, res.segment_checks))
    for it in (200, 500, 1000, 1500, 2000, 3000):
        row = res.history[it - 1]
        print("   iteration %4d: |V| = %4d, r_n = %.3f, c_best = %s" % (
            it, row[1], row[2], "inf" if not np.isfinite(row[3]) else "%.3f" % row[3]))

    # 5. plain RRT never improves; informed and k-nearest variants --------
    plain = rrt_plain(world, start, goal, eta=1.0, p_goal=0.05,
                      max_iters=3000, seed=1)
    cp = plain.history[:, 3]
    assert plain.path is not None and path_is_free(world, plain.path)
    assert np.all(cp[np.isfinite(cp)] == plain.cost)
    inf_res = rrt_star(world, start, goal, eta=1.0, gamma=gamma, p_goal=0.05,
                       max_iters=3000, seed=1, informed=True)
    assert inf_res.path is not None and path_is_free(world, inf_res.path)
    ci = inf_res.history[:, 3]
    assert np.all(np.diff(ci[np.isfinite(ci)]) <= 1e-12)
    assert inf_res.cost <= 1.05 * ref_len
    knn_res = rrt_star(world, start, goal, eta=1.0, p_goal=0.05,
                       max_iters=2000, seed=1, knn=True)
    assert knn_res.path is not None and path_is_free(world, knn_res.path)
    assert knn_res.tree.costs_consistent()
    print("RRT (seed 1): first and only cost %.3f; Informed RRT*: %.3f "
          "(%d of %d informed draws rejected); k-nearest RRT* after 2000 "
          "iterations: %.3f (k_n = %d at |V| = %d)"
          % (plain.cost, inf_res.cost, inf_res.sampler.rejections,
             inf_res.sampler.draws, knn_res.cost,
             knn_count(knn_res.tree.n, 2), knn_res.tree.n))
    # the wide field: the informed set is a small part of X
    wide = wide_example_world()
    assert abs(free_volume(wide) - 876.0) < 5.0
    wr = rrt_star(wide, start, goal, eta=1.0, gamma=45.0, p_goal=0.05,
                  max_iters=3000, seed=1)
    wi = rrt_star(wide, start, goal, eta=1.0, gamma=45.0, p_goal=0.05,
                  max_iters=3000, seed=1, informed=True)
    for r in (wr, wi):
        assert r.path is not None and path_is_free(wide, r.path)
        cc = r.history[:, 3]
        assert np.all(np.diff(cc[np.isfinite(cc)]) <= 1e-12)
    pts = np.array([wi.sampler.sample(rng, wi.cost, wide) for _ in range(300)])
    assert np.all(np.linalg.norm(pts - start, axis=1)
                  + np.linalg.norm(pts - goal, axis=1) <= wi.cost + 1e-9)
    print("wide field (seed 1): RRT* %.3f, Informed RRT* %.3f after 3000 "
          "iterations; informed set is %.0f%% of X at the end" % (
              wr.cost, wi.cost, 100 * wi.sampler.measure(wi.cost) / wide.volume()))

    # 6. the same code in 3D ----------------------------------------------
    w3 = scene_3d()
    s3, g3 = np.array([0.5, 0.5, 0.5]), np.array([9.5, 9.5, 9.5])
    r3 = rrt_star(w3, s3, g3, eta=1.5, p_goal=0.05, max_iters=1500, seed=3,
                  informed=True)
    assert r3.path is not None and path_is_free(w3, r3.path)
    assert r3.tree.costs_consistent()
    c3 = r3.history[:, 3]
    assert np.all(np.diff(c3[np.isfinite(c3)]) <= 1e-12)
    print("3D (seed 3): first solution at iteration %d, cost %.2f -> %.2f "
          "after 1500 iterations; straight line %.2f; gamma = %.1f"
          % (r3.solution_iter, c3[np.isfinite(c3)][0], r3.cost,
             np.linalg.norm(g3 - s3), r3.gamma))
    print("self-test passed in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    _self_test()
