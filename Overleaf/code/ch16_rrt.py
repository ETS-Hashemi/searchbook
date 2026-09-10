"""Rapidly-exploring random trees for chapter 16.

RRT, RRT-Connect, a kinodynamic RRT for the double-integrator drone and
path shortcutting, in 2D or 3D worlds with axis-aligned box and sphere
obstacles.  NumPy only, ASCII only.

    python3 ch16_rrt.py        runs the self-test (a few seconds)

Conventions
-----------
* A configuration q is a NumPy array of length d (d = 2 or 3); the
  configuration space C is the box [lower, upper].
* The robot is a sphere of radius `radius`.  A configuration is free if
  it lies inside C and its distance to every obstacle exceeds `radius`.
* Segments are checked by subdivision: points spaced at most `delta`
  apart are tested against the box obstacles inflated by
  radius + delta/2, which guarantees a clearance of at least `radius`
  along the whole segment (the resolution argument in the text).
  Sphere obstacles are tested exactly with the segment-sphere test of
  chapter 2 (distance from the center to the segment).
* Nearest neighbors are found by a vectorized linear scan (no kd-tree);
  the trees of this chapter have a few thousand vertices at most.
"""
import math
import time

import numpy as np

TRAPPED, ADVANCED, REACHED = "trapped", "advanced", "reached"


# ----------------------------------------------------------------------
# The world: configuration space, obstacles and collision checks
# ----------------------------------------------------------------------
class World:
    """Box-shaped configuration space with box and sphere obstacles."""

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
        self.point_checks = 0

    def sample(self, rng):
        """A configuration drawn uniformly from C (free or not)."""
        return self.lower + rng.random(self.dim) * (self.upper - self.lower)

    def box_distances(self, pts):
        """Distance from each point (m, d) to each box, shape (m, nb).

        Sphere-versus-box test: clamp the point into the box; the length
        of the clamping vector is the distance (0 inside the box)."""
        p = pts[:, None, :]
        gap = np.maximum(np.maximum(self.box_lo[None] - p,
                                    p - self.box_hi[None]), 0.0)
        return np.sqrt((gap ** 2).sum(axis=2))

    def points_free(self, pts, margin=None, spheres=True):
        """Boolean array: is each point inside C and further than `margin`
        (default: the robot radius) from every obstacle?"""
        pts = np.atleast_2d(np.asarray(pts, dtype=float))
        margin = self.radius if margin is None else margin
        self.point_checks += len(pts)
        ok = np.all((pts >= self.lower) & (pts <= self.upper), axis=1)
        if len(self.box_lo):
            ok &= np.all(self.box_distances(pts) > margin, axis=1)
        if spheres and len(self.sph_c):
            d = np.linalg.norm(pts[:, None, :] - self.sph_c[None], axis=2)
            ok &= np.all(d > self.sph_r + margin, axis=1)
        return ok

    def point_free(self, q):
        return bool(self.points_free(q)[0])

    def segment_free(self, a, b):
        """CollisionFree(a, b): subdivision check of the straight segment.

        Points spaced at most delta apart are tested against the boxes
        inflated by radius + delta/2 (conservative: every point of the
        segment is within delta/2 of a tested point, so the true clearance
        is at least radius).  Spheres use the exact segment-sphere test."""
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


# ----------------------------------------------------------------------
# The tree and the primitives
# ----------------------------------------------------------------------
class Tree:
    """Vertices in a growing array, parent indices, nearest by a scan."""

    def __init__(self, root, capacity=1024):
        root = np.asarray(root, dtype=float)
        self.V = np.zeros((max(int(capacity), 8), len(root)))
        self.parent = np.full(len(self.V), -1, dtype=int)
        self.V[0] = root
        self.n = 1

    def nearest(self, q):
        """Index of the vertex closest to q (Euclidean, linear scan)."""
        d2 = ((self.V[:self.n] - q) ** 2).sum(axis=1)
        return int(np.argmin(d2))

    def add(self, q, parent):
        if self.n == len(self.V):
            self.V = np.vstack([self.V, np.zeros_like(self.V)])
            self.parent = np.concatenate(
                [self.parent, np.full(len(self.parent), -1, dtype=int)])
        self.V[self.n] = q
        self.parent[self.n] = parent
        self.n += 1
        return self.n - 1

    def path_to(self, i):
        """Configurations from the root to vertex i, shape (k, d)."""
        idx = []
        while i >= 0:
            idx.append(i)
            i = self.parent[i]
        return self.V[idx[::-1]].copy()

    def edges(self):
        return [(int(self.parent[i]), i) for i in range(1, self.n)]


def steer(q_near, q_rand, eta):
    """Move from q_near toward q_rand by at most eta."""
    d = q_rand - q_near
    dist = np.linalg.norm(d)
    if dist <= eta:
        return q_rand.copy()
    return q_near + (eta / dist) * d


def extend(tree, world, q, eta):
    """One extension of `tree` toward q.

    Returns (status, index): REACHED if q itself became (or already was)
    a vertex, ADVANCED if a new vertex was added short of q, TRAPPED if
    the segment was blocked (index -1)."""
    i_near = tree.nearest(q)
    q_near = tree.V[i_near]
    if np.linalg.norm(q - q_near) < 1e-12:
        return REACHED, i_near
    q_new = steer(q_near, q, eta)
    if not world.segment_free(q_near, q_new):
        return TRAPPED, -1
    i_new = tree.add(q_new, i_near)
    if np.linalg.norm(q_new - q) < 1e-12:
        return REACHED, i_new
    return ADVANCED, i_new


class Result:
    """Attribute bag returned by the planners."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


# ----------------------------------------------------------------------
# RRT
# ----------------------------------------------------------------------
def rrt(world, start, goal, eta=0.5, p_goal=0.05, r_goal=0.5,
        max_iters=2000, seed=0, stop_at_goal=True, snapshots=(),
        trace=None):
    """Plain RRT with goal bias and a goal region of radius r_goal.

    Returns a Result with .path (array of configurations from start to
    goal, or None), .iterations (samples drawn), .solution_iter (the
    iteration at which the goal region was entered), .tree and
    .snapshots (iteration -> number of vertices at that iteration).
    With stop_at_goal=False the tree keeps growing after the first
    solution, which is used for the figures."""
    rng = np.random.default_rng(seed)
    start = np.asarray(start, dtype=float)
    goal = np.asarray(goal, dtype=float)
    tree = Tree(start, max_iters + 2)
    goal_index, solution_iter, snaps = -1, None, {}
    it = 0
    for it in range(1, max_iters + 1):
        q_rand = goal if rng.random() < p_goal else world.sample(rng)
        i_near = tree.nearest(q_rand)
        q_near = tree.V[i_near]
        q_new = steer(q_near, q_rand, eta)
        free = world.segment_free(q_near, q_new)
        if trace is not None:
            trace.append((it, q_rand.copy(), i_near, q_new.copy(), free))
        if free and np.linalg.norm(q_new - q_near) > 1e-12:
            i_new = tree.add(q_new, i_near)
            if goal_index < 0 and np.linalg.norm(q_new - goal) <= r_goal:
                goal_index, solution_iter = i_new, it
                if stop_at_goal:
                    break
        if it in snapshots:
            snaps[it] = tree.n
    path = None
    if goal_index >= 0:
        path = tree.path_to(goal_index)
        if (np.linalg.norm(path[-1] - goal) > 0
                and world.segment_free(path[-1], goal)):
            path = np.vstack([path, goal])
    return Result(path=path, iterations=it, solution_iter=solution_iter,
                  tree=tree, snapshots=snaps, n_vertices=tree.n)


# ----------------------------------------------------------------------
# RRT-Connect
# ----------------------------------------------------------------------
def connect(tree, world, q, eta):
    """Repeat extend toward q until q is reached or the tree is trapped."""
    while True:
        status, i = extend(tree, world, q, eta)
        if status != ADVANCED:
            return status, i


def rrt_connect(world, start, goal, eta=0.5, max_iters=2000, seed=0):
    """RRT-Connect: a tree from the start and a tree from the goal, the
    greedy Connect step, and the roles of the trees swapped every
    iteration (Kuffner and LaValle 2000).  Same Result fields as rrt();
    .tree is the start tree and .tree_goal the goal tree."""
    rng = np.random.default_rng(seed)
    start = np.asarray(start, dtype=float)
    goal = np.asarray(goal, dtype=float)
    t_start, t_goal = Tree(start, max_iters + 2), Tree(goal, max_iters + 2)
    t_a, t_b = t_start, t_goal
    for it in range(1, max_iters + 1):
        q_rand = world.sample(rng)
        status, i_new = extend(t_a, world, q_rand, eta)
        if status != TRAPPED:
            q_new = t_a.V[i_new]
            status_b, i_b = connect(t_b, world, q_new, eta)
            if status_b == REACHED:
                path_a, path_b = t_a.path_to(i_new), t_b.path_to(i_b)
                if t_a is t_start:
                    path = np.vstack([path_a, path_b[::-1][1:]])
                else:
                    path = np.vstack([path_b, path_a[::-1][1:]])
                return Result(path=path, iterations=it, solution_iter=it,
                              tree=t_start, tree_goal=t_goal,
                              n_vertices=t_start.n + t_goal.n)
        t_a, t_b = t_b, t_a
    return Result(path=None, iterations=max_iters, solution_iter=None,
                  tree=t_start, tree_goal=t_goal,
                  n_vertices=t_start.n + t_goal.n)


# ----------------------------------------------------------------------
# Kinodynamic RRT for the double integrator
# ----------------------------------------------------------------------
def random_in_ball(rng, d, r):
    """A point drawn uniformly from the ball of radius r in R^d."""
    u = rng.normal(size=d)
    u /= np.linalg.norm(u)
    return u * r * rng.random() ** (1.0 / d)


def kinodynamic_rrt(world, start, goal, v_max=2.0, a_max=2.0, dt=0.5,
                    n_controls=8, r_goal=0.5, p_goal=0.05, w_vel=0.5,
                    max_iters=4000, seed=0):
    """Kinodynamic RRT for the double integrator of chapter 2.

    The state is x = (p, v); the control is a constant acceleration a
    with |a| <= a_max held for dt (zero-order hold), and |v| <= v_max.
    Steer is replaced by trying n_controls random accelerations and
    keeping the one whose result is closest to the sampled state; Nearest
    uses the weighted metric |dp|^2 + w_vel^2 |dv|^2.  Returns a Result
    with .states (k, 2d), .controls (k-1, d), .iterations, .n_vertices."""
    rng = np.random.default_rng(seed)
    d = world.dim
    goal = np.asarray(goal, dtype=float)
    X = np.zeros((max_iters + 2, 2 * d))
    X[0, :d] = np.asarray(start, dtype=float)
    U = np.zeros((max_iters + 2, d))
    parent = np.full(max_iters + 2, -1, dtype=int)
    w = np.concatenate([np.ones(d), w_vel * np.ones(d)])
    n, goal_index, it = 1, -1, 0
    for it in range(1, max_iters + 1):
        if rng.random() < p_goal:
            x_rand = np.concatenate([goal, np.zeros(d)])
        else:
            x_rand = np.concatenate([world.sample(rng),
                                     random_in_ball(rng, d, v_max)])
        i_near = int(np.argmin((((X[:n] - x_rand) * w) ** 2).sum(axis=1)))
        p, v = X[i_near, :d], X[i_near, d:]
        best, best_a, best_d2 = None, None, np.inf
        for _ in range(n_controls):
            a = random_in_ball(rng, d, a_max)
            v_new = v + dt * a
            if np.linalg.norm(v_new) > v_max:
                continue
            # the speed along a constant-acceleration arc is largest at an
            # endpoint, so this many points are at most delta apart
            m = int(math.ceil(max(np.linalg.norm(v), np.linalg.norm(v_new))
                              * dt / world.delta)) + 1
            ts = np.linspace(0.0, dt, m + 1)[:, None]
            pts = p + ts * v + 0.5 * ts ** 2 * a
            if not np.all(world.points_free(
                    pts, world.radius + 0.5 * world.delta)):
                continue
            x_new = np.concatenate([pts[-1], v_new])
            d2 = float((((x_new - x_rand) * w) ** 2).sum())
            if d2 < best_d2:
                best, best_a, best_d2 = x_new, a, d2
        if best is None:
            continue
        X[n], U[n], parent[n] = best, best_a, i_near
        n += 1
        if np.linalg.norm(best[:d] - goal) <= r_goal:
            goal_index = n - 1
            break
    states = controls = None
    if goal_index >= 0:
        idx = []
        i = goal_index
        while i >= 0:
            idx.append(i)
            i = parent[i]
        idx = idx[::-1]
        states, controls = X[idx].copy(), U[idx[1:]].copy()
    return Result(states=states, controls=controls, iterations=it,
                  n_vertices=n, dt=dt)


# ----------------------------------------------------------------------
# Path post-processing
# ----------------------------------------------------------------------
def path_length(path):
    path = np.asarray(path, dtype=float)
    return float(np.linalg.norm(np.diff(path, axis=0), axis=1).sum())


def _point_on_path(path, cum, s):
    """Point at arc length s along the polyline and its segment index."""
    k = int(np.clip(np.searchsorted(cum, s, side="right") - 1,
                    0, len(path) - 2))
    seg = cum[k + 1] - cum[k]
    t = 0.0 if seg <= 0 else (s - cum[k]) / seg
    return path[k] + t * (path[k + 1] - path[k]), k


def shortcut(path, world, n_tries=100, seed=0):
    """Random shortcutting: pick two random points on the path; if the
    straight segment between them is free, replace the part in between.
    The triangle inequality guarantees that the length never grows."""
    path = np.asarray(path, dtype=float)
    rng = np.random.default_rng(seed)
    for _ in range(n_tries):
        if len(path) < 3:
            break
        cum = np.concatenate(
            [[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
        s1, s2 = np.sort(rng.random(2) * cum[-1])
        p1, k1 = _point_on_path(path, cum, s1)
        p2, k2 = _point_on_path(path, cum, s2)
        if k2 <= k1:
            continue  # both points on one segment: already straight
        if world.segment_free(p1, p2):
            path = np.vstack([path[:k1 + 1], p1, p2, path[k2 + 1:]])
            keep = np.concatenate(
                [[True], np.linalg.norm(np.diff(path, axis=0), axis=1) > 1e-9])
            path = path[keep]
    return path


def prune(path, world):
    """Greedy pruning: from the current vertex jump to the furthest later
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


def visibility_shortest_path(world, start, goal, offset=0.05):
    """Reference shortest path in 2D among boxes: Dijkstra on the visibility
    graph of the box corners pushed outward by the inflation plus `offset`
    (a slightly conservative estimate of the optimal length)."""
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
    dist = np.full(n, np.inf)
    prev = np.full(n, -1, dtype=int)
    done = np.zeros(n, dtype=bool)
    dist[0] = 0.0
    for _ in range(n):
        cand = np.where(done, np.inf, dist)
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
        return None, np.inf
    idx, i = [], 1
    while i >= 0:
        idx.append(i)
        i = prev[i]
    return np.array([pts[k] for k in idx[::-1]]), float(dist[1])


# ----------------------------------------------------------------------
# Test scenes
# ----------------------------------------------------------------------
def worked_example_world():
    """The 2D map of the worked example: two rectangular walls."""
    return World([0, 0], [10, 10],
                 boxes=[([3, 0], [5, 6]), ([6, 4], [8, 10])],
                 radius=0.0, delta=0.05)


def scene_3d():
    """A 3D box field: a wall, a full-height pillar, a slab and blocks."""
    boxes = [([2, 0, 0], [3, 10, 6]),     # wall, fly over it
             ([5, 3, 0], [6, 7, 10]),     # full-height pillar
             ([7, 0, 4], [8, 10, 5]),     # slab, fly under or over
             ([4, 7, 0], [9, 9, 3]),      # low block
             ([0, 4, 7], [4, 6, 8]),      # beam near the ceiling
             ([8, 2, 6], [10, 4, 10])]    # high block in the corner
    return World([0, 0, 0], [10, 10, 10], boxes=boxes, radius=0.3, delta=0.1)


def path_is_free(world, path, factor=10):
    """Check a path with a `factor` times finer subdivision."""
    fine = World(world.lower, world.upper,
                 boxes=list(zip(world.box_lo, world.box_hi)),
                 spheres=list(zip(world.sph_c, world.sph_r)),
                 radius=world.radius, delta=world.delta / factor)
    return all(fine.segment_free(path[k], path[k + 1])
               for k in range(len(path) - 1))


def iterations_over_seeds(world, start, goal, planner, seeds, **kw):
    """List of solution iterations (None = failure) over the seeds."""
    out = []
    for s in seeds:
        res = planner(world, start, goal, seed=s, **kw)
        out.append(res.solution_iter)
    return out


# ----------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------
def _self_test():
    t0 = time.time()
    # 1. collision checks -------------------------------------------------
    w = World([0, 0], [10, 10], boxes=[([4, 0], [4.02, 10])],
              spheres=[([8, 8], 1.0)], radius=0.0, delta=0.05)
    assert not w.point_free(np.array([4.01, 5.0]))
    assert w.point_free(np.array([3.5, 5.0]))
    # the wall is thinner than delta, but the inflation by delta/2 makes it
    # impossible for all test points to miss it, at any angle: sweep 40
    # segment directions through a point inside the wall, then 40 parallel
    # crossings of it
    c = np.array([4.01, 5.0])
    for th in np.linspace(0.0, np.pi, 40, endpoint=False):
        e = 2.0 * np.array([math.cos(th), math.sin(th)])
        assert not w.segment_free(c - e, c + e)
    for y in np.linspace(0.3, 9.7, 40):
        assert not w.segment_free([1.0, y], [7.0, y + 0.3])
    assert w.segment_free([1, 1], [3.9, 9])
    assert not w.segment_free([6, 8], [9.5, 8])       # through the sphere
    assert w.segment_free([6, 9.2], [9.5, 9.2])       # just past it
    assert not w.segment_free([6, 9.0], [9.5, 9.0])   # tangent: blocked
    wb = World([0, 0], [10, 10], boxes=[([3, 3], [5, 5])], radius=0.5)
    assert wb.point_free(np.array([2.4, 2.4]))        # corner distance 0.85
    assert not wb.point_free(np.array([2.7, 2.7]))    # corner distance 0.42
    print("collision checks ok")

    # 2. the worked example -----------------------------------------------
    world = worked_example_world()
    start, goal = np.array([1.0, 1.0]), np.array([9.0, 9.0])
    trace = []
    res = rrt(world, start, goal, eta=0.5, p_goal=0.05, r_goal=0.5,
              max_iters=2000, seed=1, trace=trace)
    n_checks = world.point_checks
    assert res.path is not None
    assert path_is_free(world, res.path)
    assert np.allclose(res.path[0], start) and np.allclose(res.path[-1], goal)
    steps = np.linalg.norm(np.diff(res.path, axis=0), axis=1)
    assert np.all(steps <= 0.5 + 1e-9) and np.all(steps > 0)
    res2 = rrt(world, start, goal, eta=0.5, p_goal=0.05, r_goal=0.5,
               max_iters=2000, seed=1)
    assert np.array_equal(res.path, res2.path)         # deterministic
    print("worked example: solution at iteration %d, %d vertices, "
          "%d path vertices, length %.3f, %d point tests" % (
              res.solution_iter, res.n_vertices, len(res.path),
              path_length(res.path), n_checks))
    print("first iterations (it, q_rand, nearest, q_new, free):")
    for (it, q_rand, i_near, q_new, free) in trace[:10]:
        print("  %2d  (%.2f, %.2f)  %2d  (%.2f, %.2f)  %s" % (
            it, q_rand[0], q_rand[1], i_near, q_new[0], q_new[1], free))
    blocked = [t[0] for t in trace if not t[4]]
    print("  first blocked extension at iteration %s; %d of %d blocked"
          % (blocked[0] if blocked else None, len(blocked), len(trace)))
    ref_path, ref_len = visibility_shortest_path(world, start, goal)
    clearance = world.radius + 0.5 * world.delta + 0.05
    print("  visibility-graph shortest path length %.3f via %d vertices "
          "(clearance %.3f)" % (ref_len, len(ref_path), clearance))
    # the same reference in the limit of zero clearance: the corner offset
    # only keeps the visibility edges free, so push the interior waypoints
    # back onto the exact corners and measure the polyline again
    w0 = World([0, 0], [10, 10], boxes=[([3, 0], [5, 6]), ([6, 4], [8, 10])],
               radius=0.0, delta=0.01)
    p0, _ = visibility_shortest_path(w0, start, goal, offset=0.005)
    corners = np.array([[x, y] for lo, hi in zip(w0.box_lo, w0.box_hi)
                        for x in (lo[0], hi[0]) for y in (lo[1], hi[1])])
    p0[1:-1] = corners[np.argmin(
        ((p0[1:-1, None, :] - corners[None, :, :]) ** 2).sum(axis=2), axis=1)]
    ref0 = path_length(p0)
    print("  zero-clearance shortest path length %.3f via %s" % (
        ref0, " ".join("(%g,%g)" % tuple(c) for c in p0[1:-1])))
    assert ref0 < ref_len
    assert path_length(res.path) > ref_len

    # 3. smoothing never increases the length -----------------------------
    raw_len = path_length(res.path)
    sc = shortcut(res.path, world, n_tries=100, seed=0)
    pr = prune(res.path, world)
    assert path_length(sc) <= raw_len + 1e-9 and path_is_free(world, sc)
    assert path_length(pr) <= raw_len + 1e-9 and path_is_free(world, pr)
    assert np.allclose(sc[0], start) and np.allclose(sc[-1], goal)
    assert np.allclose(pr[0], start) and np.allclose(pr[-1], goal)
    print("smoothing: raw %.3f, shortcut %.3f (%d vertices), prune %.3f "
          "(%d vertices), reference %.3f" % (
              raw_len, path_length(sc), len(sc), path_length(pr), len(pr),
              ref_len))

    # 4. RRT-Connect needs fewer iterations than RRT (over seeds) ---------
    seeds = range(40)
    it_rrt = iterations_over_seeds(world, start, goal, rrt, seeds, eta=0.5,
                                   p_goal=0.05, r_goal=0.5, max_iters=3000)
    it_con = iterations_over_seeds(world, start, goal, rrt_connect, seeds,
                                   eta=0.5, max_iters=3000)
    assert all(x is not None for x in it_rrt) and \
        all(x is not None for x in it_con)
    m_rrt, m_con = np.median(it_rrt), np.median(it_con)
    assert m_con < m_rrt and np.mean(it_con) < np.mean(it_rrt)
    print("iterations over %d seeds: RRT median %.0f (mean %.0f), "
          "RRT-Connect median %.0f (mean %.0f)" % (
              len(seeds), m_rrt, np.mean(it_rrt), m_con, np.mean(it_con)))
    for s in range(5):
        rc = rrt_connect(world, start, goal, eta=0.5, seed=s)
        assert rc.path is not None and path_is_free(world, rc.path)
        assert np.allclose(rc.path[0], start) and np.allclose(rc.path[-1], goal)
        assert np.all(np.linalg.norm(np.diff(rc.path, axis=0), axis=1)
                      <= 0.5 + 1e-9)
        assert path_length(shortcut(rc.path, world)) <= path_length(rc.path) + 1e-9

    # 5. the same code in 3D: only the world changes ----------------------
    w3 = scene_3d()
    s3, g3 = np.array([0.5, 0.5, 0.5]), np.array([9.5, 9.5, 9.5])
    r3 = rrt(w3, s3, g3, eta=0.8, p_goal=0.05, r_goal=0.5, max_iters=4000,
             seed=3)
    assert r3.path is not None and path_is_free(w3, r3.path)
    sc3 = shortcut(r3.path, w3, n_tries=100, seed=0)
    assert path_length(sc3) <= path_length(r3.path) + 1e-9
    assert path_is_free(w3, sc3)
    c3 = rrt_connect(w3, s3, g3, eta=0.8, max_iters=4000, seed=3)
    assert c3.path is not None and path_is_free(w3, c3.path)
    print("3D: RRT solution at iteration %d with %d vertices, length %.2f "
          "(shortcut %.2f); RRT-Connect at iteration %d, %d vertices, "
          "length %.2f; straight line %.2f" % (
              r3.solution_iter, r3.n_vertices, path_length(r3.path),
              path_length(sc3), c3.iterations, c3.n_vertices,
              path_length(c3.path), np.linalg.norm(g3 - s3)))

    # 6. kinodynamic RRT: the path obeys the double integrator ------------
    kr = kinodynamic_rrt(world, start, goal, v_max=2.0, a_max=2.0, dt=0.5,
                         seed=2)
    assert kr.states is not None
    d, dt = 2, kr.dt
    A = np.block([[np.eye(d), dt * np.eye(d)], [np.zeros((d, d)), np.eye(d)]])
    B = np.vstack([0.5 * dt ** 2 * np.eye(d), dt * np.eye(d)])
    for k in range(len(kr.controls)):
        assert np.allclose(kr.states[k + 1], A @ kr.states[k] + B @ kr.controls[k])
        assert np.linalg.norm(kr.controls[k]) <= 2.0 + 1e-9
        assert np.linalg.norm(kr.states[k + 1, d:]) <= 2.0 + 1e-9
    assert np.linalg.norm(kr.states[-1, :d] - goal) <= 0.5
    print("kinodynamic: solution at iteration %d, %d vertices, %d steps "
          "(%.1f s of flight), final speed %.2f" % (
              kr.iterations, kr.n_vertices, len(kr.controls),
              len(kr.controls) * dt, np.linalg.norm(kr.states[-1, d:])))
    # 7. cost of the linear-scan nearest-neighbor query ------------------
    rng = np.random.default_rng(0)
    timings = []
    for n in (10 ** 3, 10 ** 4, 10 ** 5):
        tr = Tree(np.zeros(3), capacity=n)
        tr.V = rng.random((n, 3)) * 10.0
        tr.n = n
        qs = rng.random((200, 3)) * 10.0
        t1 = time.time()
        for q in qs:
            tr.nearest(q)
        timings.append((n, 1e3 * (time.time() - t1) / len(qs)))
    assert timings[-1][1] > timings[0][1]
    print("nearest by linear scan (3D, mean of 200 queries): " + ", ".join(
        "n=%d %.3f ms" % (n, ms) for n, ms in timings))

    print("self-test passed in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    _self_test()
