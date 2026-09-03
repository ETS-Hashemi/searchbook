"""Chapter 2 -- The Toolbox.

Grids, space-time states, plan costs, motion models, 2D geometry,
covariance ellipses and a lazy-deletion priority queue.  Later chapters
import from this file or copy its idioms.

Run the self-test with

    python3 ch02_toolbox.py

Geometry works on plain tuples of floats (so that positions can be used
as dictionary keys); NumPy is used for the linear algebra only.
"""
from __future__ import annotations

import heapq
import itertools
import math

import numpy as np

SQRT2 = math.sqrt(2.0)

# ---------------------------------------------------------------------
# 1. Grids
# ---------------------------------------------------------------------
MOVES4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
MOVES8 = MOVES4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


class Grid:
    """A 2D occupancy grid.

    Cells are integer pairs (x, y) with 0 <= x < width, 0 <= y < height.
    ``connectivity`` is 4 or 8.  With 8-connectivity a diagonal move is
    allowed only if both cells it cuts across are free (corner-cutting rule).
    """

    def __init__(self, width, height, obstacles=(), connectivity=4):
        if connectivity not in (4, 8):
            raise ValueError("connectivity must be 4 or 8")
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.connectivity = connectivity

    @classmethod
    def from_strings(cls, rows, connectivity=4):
        """Build a grid from an ASCII map: '.' free, '#' blocked.

        rows[0] is the top row of the picture, so y = height - 1 - row.
        """
        height, width = len(rows), len(rows[0])
        obstacles = set()
        for i, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "#":
                    obstacles.add((x, height - 1 - i))
        return cls(width, height, obstacles, connectivity)

    def to_strings(self):
        """Inverse of ``from_strings``."""
        rows = []
        for y in range(self.height - 1, -1, -1):
            rows.append("".join("#" if (x, y) in self.obstacles else "."
                                for x in range(self.width)))
        return rows

    def in_bounds(self, cell):
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def is_free(self, cell):
        return self.in_bounds(cell) and cell not in self.obstacles

    def neighbors(self, cell):
        """Return [(neighbour, cost)] for the free neighbours of ``cell``."""
        x, y = cell
        moves = MOVES4 if self.connectivity == 4 else MOVES8
        result = []
        for dx, dy in moves:
            nxt = (x + dx, y + dy)
            if not self.is_free(nxt):
                continue
            if dx != 0 and dy != 0:                     # diagonal move
                if not (self.is_free((x + dx, y))
                        and self.is_free((x, y + dy))):
                    continue                            # corner cutting
                result.append((nxt, SQRT2))
            else:
                result.append((nxt, 1.0))
        return result

    def inflate(self, radius):
        """Return a copy in which every cell whose centre lies within
        ``radius`` (cell units) of an obstacle square is also blocked.

        This samples the Minkowski sum of the obstacle squares with a
        disc of radius ``radius`` at the cell centres.
        """
        reach = int(math.ceil(radius + 0.5))
        blocked = set(self.obstacles)
        for (ox, oy) in self.obstacles:
            for dx in range(-reach, reach + 1):
                for dy in range(-reach, reach + 1):
                    cell = (ox + dx, oy + dy)
                    if not self.in_bounds(cell):
                        continue
                    # distance from the centre of ``cell`` to the unit
                    # square [ox - 1/2, ox + 1/2] x [oy - 1/2, oy + 1/2]
                    ex = max(abs(dx) - 0.5, 0.0)
                    ey = max(abs(dy) - 0.5, 0.0)
                    if math.hypot(ex, ey) <= radius:
                        blocked.add(cell)
        return Grid(self.width, self.height, blocked, self.connectivity)


def lattice_stretch(dim, diagonals=True):
    """Worst-case ratio between the cost of the cheapest lattice path and
    the straight-line distance in an empty ``dim``-dimensional lattice.

    With diagonal moves, a displacement with sorted absolute components
    a_1 >= ... >= a_d >= 0 costs sum_k (a_k - a_{k+1}) sqrt(k); maximising
    the ratio over all directions (Cauchy-Schwarz) gives
    sqrt(sum_k (sqrt(k) - sqrt(k - 1))^2).  Without diagonals it is sqrt(d).
    """
    if not diagonals:
        return math.sqrt(dim)
    return math.sqrt(sum((math.sqrt(k) - math.sqrt(k - 1)) ** 2
                         for k in range(1, dim + 1)))


def lattice_path_cost(displacement):
    """Cost of the cheapest path to ``displacement`` in an empty lattice
    with all diagonal moves (cost sqrt(k) for k non-zero components)."""
    a = sorted((abs(x) for x in displacement), reverse=True) + [0]
    return sum((a[k] - a[k + 1]) * math.sqrt(k + 1) for k in range(len(a) - 1))


# ---------------------------------------------------------------------
# 2. Space-time states and plans
# ---------------------------------------------------------------------
def space_time_successors(grid, state, wait_cost=1.0):
    """Successors of the space-time state (cell, t): wait or move to a
    neighbour, all at time t + 1.  Moves carry the grid's edge cost."""
    cell, t = state
    succ = [((cell, t + 1), wait_cost)]                 # wait action
    for nxt, cost in grid.neighbors(cell):
        succ.append(((nxt, t + 1), cost))
    return succ


def path_length(path):
    """Euclidean length of the polyline through the visited cell centres.
    Waiting adds nothing."""
    return sum(math.dist(a, b) for a, b in zip(path, path[1:]))


def path_time(path):
    """Cost of a time-indexed path: the number of time steps until the
    agent reaches its last cell and never leaves it again."""
    goal = path[-1]
    t = len(path) - 1
    while t > 0 and path[t - 1] == goal:
        t -= 1
    return t


def makespan(plan):
    """Makespan of a plan (a list of time-indexed paths)."""
    return max(path_time(path) for path in plan)


def sum_of_costs(plan):
    """Sum of costs of a plan (a list of time-indexed paths)."""
    return sum(path_time(path) for path in plan)


def position_at(path, t):
    """Cell of an agent at integer time t; agents stay at their last cell."""
    return path[min(t, len(path) - 1)]


def min_separation(plan):
    """Smallest centre distance between two agents at any integer time."""
    horizon = max(len(path) for path in plan) - 1
    best = math.inf
    for t in range(horizon + 1):
        for i in range(len(plan)):
            for j in range(i + 1, len(plan)):
                d = math.dist(position_at(plan[i], t), position_at(plan[j], t))
                best = min(best, d)
    return best


def min_separation_continuous(plan):
    """Smallest distance when agents move in straight lines between
    consecutive time steps (time of closest approach on each interval)."""
    horizon = max(len(path) for path in plan) - 1
    best = math.inf
    for t in range(horizon):
        for i in range(len(plan)):
            for j in range(i + 1, len(plan)):
                pa, pb = position_at(plan[i], t), position_at(plan[j], t)
                va = sub(position_at(plan[i], t + 1), pa)
                vb = sub(position_at(plan[j], t + 1), pb)
                _, d = time_of_closest_approach(pa, va, pb, vb, horizon=1.0)
                best = min(best, d)
    return best


# ---------------------------------------------------------------------
# 3. Geometry in the plane
# ---------------------------------------------------------------------
def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def scale(a, s):
    return (a[0] * s, a[1] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    """The 2D cross product a_x b_y - a_y b_x (signed area, left turn > 0)."""
    return a[0] * b[1] - a[1] * b[0]


def norm(a):
    return math.hypot(a[0], a[1])


def point_segment_distance(p, a, b):
    """Distance from p to the segment ab.  Returns (distance, closest
    point q, parameter s in [0, 1] with q = a + s (b - a))."""
    ab = sub(b, a)
    len2 = dot(ab, ab)
    if len2 == 0.0:
        s = 0.0
    else:
        s = max(0.0, min(1.0, dot(sub(p, a), ab) / len2))
    q = add(a, scale(ab, s))
    return norm(sub(p, q)), q, s


def ray_circle_intersection(o, d, c, r):
    """Smallest t >= 0 with |o + t d - c| = r, or None if the ray misses
    the circle.  Returns 0.0 if o already lies inside the circle."""
    f = sub(o, c)
    a = dot(d, d)
    b = dot(f, d)
    k = dot(f, f) - r * r
    if k <= 0.0:
        return 0.0
    if a == 0.0:
        return None
    disc = b * b - a * k
    if disc < 0.0:
        return None
    t = (-b - math.sqrt(disc)) / a
    return t if t >= 0.0 else None


def segment_circle_intersects(a, b, c, r):
    """True if the segment ab meets the disc of centre c and radius r."""
    return point_segment_distance(c, a, b)[0] <= r


def minkowski_disc(c1, r1, c2, r2):
    """Minkowski sum of two discs: a disc of centre c1 + c2 and radius r1 + r2."""
    return add(c1, c2), r1 + r2


def tangent_points(p, c, r):
    """The two points where the tangent lines from p touch the circle
    (c, r), or None if p lies on or inside the circle."""
    u = sub(p, c)
    d = norm(u)
    if d <= r:
        return None
    u = scale(u, 1.0 / d)                 # unit vector from c towards p
    perp = (-u[1], u[0])                  # u rotated by +90 degrees
    cos_a = r / d                         # angle at the centre
    sin_a = math.sqrt(1.0 - cos_a * cos_a)
    t_left = add(c, scale(add(scale(u, cos_a), scale(perp, sin_a)), r))
    t_right = add(c, scale(add(scale(u, cos_a), scale(perp, -sin_a)), r))
    return t_left, t_right


def time_of_closest_approach(p_a, v_a, p_b, v_b, horizon=math.inf):
    """Time t* in [0, horizon] at which two constant-velocity objects are
    closest, and their distance at that time."""
    p = sub(p_b, p_a)                     # relative position
    v = sub(v_b, v_a)                     # relative velocity
    vv = dot(v, v)
    t = 0.0 if vv == 0.0 else -dot(p, v) / vv
    t = max(0.0, min(horizon, t))
    return t, norm(add(p, scale(v, t)))


def time_to_collision(p_a, v_a, r_a, p_b, v_b, r_b):
    """First time t >= 0 at which two constant-velocity discs touch, or
    None.  This is a ray-circle test in the relative frame."""
    return ray_circle_intersection(sub(p_b, p_a), sub(v_b, v_a),
                                   (0.0, 0.0), r_a + r_b)


# ---------------------------------------------------------------------
# 4. Motion models
# ---------------------------------------------------------------------
def clip_norm(vec, limit):
    """Scale ``vec`` down so that its Euclidean norm is at most ``limit``."""
    vec = np.asarray(vec, dtype=float)
    n = np.linalg.norm(vec)
    return vec if n <= limit else vec * (limit / n)


def single_integrator_step(p, v, dt, v_max=math.inf):
    """p' = p + dt v with the speed limit applied to v."""
    return np.asarray(p, dtype=float) + dt * clip_norm(v, v_max)


def double_integrator_matrices(dt, dim=2):
    """Discrete-time A, B of the double integrator for state (p, v)."""
    eye = np.eye(dim)
    zero = np.zeros((dim, dim))
    A = np.block([[eye, dt * eye], [zero, eye]])
    B = np.vstack([0.5 * dt * dt * eye, dt * eye])
    return A, B


def double_integrator_step(x, u, dt, a_max=math.inf, v_max=math.inf):
    """One step x' = A x + B u with the limits |u| <= a_max, |v'| <= v_max.
    When no limit is active this is exactly p' = p + dt v + dt^2/2 u,
    v' = v + dt u."""
    x = np.asarray(x, dtype=float)
    dim = x.size // 2
    p, v = x[:dim], x[dim:]
    u = clip_norm(u, a_max)
    v_next = clip_norm(v + dt * u, v_max)
    p_next = p + 0.5 * dt * (v + v_next)  # trapezoid = A x + B u if unclipped
    return np.concatenate([p_next, v_next])


def stopping_distance(speed, a_max):
    """Distance needed to brake from ``speed`` to rest at deceleration a_max."""
    return speed * speed / (2.0 * a_max)


# ---------------------------------------------------------------------
# 5. Uncertainty
# ---------------------------------------------------------------------
def gaussian_pdf(x, mu, sigma):
    """Density of N(mu, sigma) at x (any dimension)."""
    x, mu, sigma = (np.asarray(v, dtype=float) for v in (x, mu, sigma))
    n = mu.size
    diff = x - mu
    maha2 = diff @ np.linalg.solve(sigma, diff)
    return math.exp(-0.5 * maha2) / math.sqrt((2 * math.pi) ** n * np.linalg.det(sigma))


def covariance_ellipse(sigma, n_sigma=1.0):
    """Axes of the n_sigma covariance ellipse of a 2x2 covariance.

    Returns (a, b, angle, vecs): semi-axes a >= b, the angle (radians)
    of the major axis and the matrix whose columns are the eigenvectors.
    """
    sigma = np.asarray(sigma, dtype=float)
    vals, vecs = np.linalg.eigh(sigma)             # ascending eigenvalues
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    if vecs[0, 0] < 0.0:                           # eigenvectors are defined
        vecs[:, 0] = -vecs[:, 0]                   # up to sign: point right
    vecs[:, 1] = (-vecs[1, 0], vecs[0, 0])         # minor axis = major + 90 deg
    a, b = n_sigma * np.sqrt(vals)
    angle = math.atan2(vecs[1, 0], vecs[0, 0])     # in (-90, 90] degrees
    return float(a), float(b), angle, vecs


def ellipse_points(mu, sigma, n_sigma=1.0, n=72):
    """Points on the n_sigma ellipse of N(mu, sigma), as an (n+1) x 2 array."""
    a, b, _, vecs = covariance_ellipse(sigma, n_sigma)
    theta = np.linspace(0.0, 2.0 * np.pi, n + 1)
    local = np.stack([a * np.cos(theta), b * np.sin(theta)])
    return (vecs @ local).T + np.asarray(mu, dtype=float)


def mahalanobis2(x, mu, sigma):
    """Squared Mahalanobis distance (x - mu)^T sigma^-1 (x - mu)."""
    diff = np.asarray(x, dtype=float) - np.asarray(mu, dtype=float)
    return float(diff @ np.linalg.solve(np.asarray(sigma, dtype=float), diff))


# ---------------------------------------------------------------------
# 6. Priority queue with lazy deletion
# ---------------------------------------------------------------------
class LazyPQ:
    """Binary-heap priority queue with lazy deletion.

    ``push`` never searches the heap: a better key for a known item is
    simply pushed as a second entry.  ``pop`` discards entries whose key
    is no longer the item's best key (they are 'stale').  Ties are broken
    by insertion order, so items themselves are never compared.
    """

    def __init__(self):
        self._heap = []
        self._best = {}                   # item -> best key pushed so far
        self._counter = itertools.count()
        self.pushes = 0
        self.stale_pops = 0

    def push(self, key, item):
        """Insert ``item`` with ``key``; ignored unless ``key`` improves."""
        if item in self._best and self._best[item] <= key:
            return False
        self._best[item] = key
        heapq.heappush(self._heap, (key, next(self._counter), item))
        self.pushes += 1
        return True

    def pop(self):
        """Remove and return (key, item) with the smallest key."""
        while self._heap:
            key, _, item = heapq.heappop(self._heap)
            if self._best.get(item) == key:
                del self._best[item]
                return key, item
            self.stale_pops += 1          # stale entry: skip it
        raise IndexError("pop from an empty LazyPQ")

    def peek_key(self):
        while self._heap and self._best.get(self._heap[0][2]) != self._heap[0][0]:
            heapq.heappop(self._heap)
            self.stale_pops += 1
        return self._heap[0][0] if self._heap else None

    def __len__(self):
        return len(self._best)

    def __contains__(self, item):
        return item in self._best


# ---------------------------------------------------------------------
# Worked example of the chapter (numbers quoted in the text)
# ---------------------------------------------------------------------
def worked_example(verbose=True):
    """Two agents on a 4 x 3 grid; returns the numbers quoted in Chapter 2."""
    grid = Grid(4, 3, obstacles=(), connectivity=4)
    path1 = [(0, 1), (1, 1), (2, 1), (3, 1)]
    path2_bad = [(1, 2), (1, 1), (1, 0)]
    path2 = [(1, 2), (1, 2), (1, 1), (1, 0)]      # waits one step
    plan_bad = [path1, path2_bad]
    plan = [path1, path2]
    out = {
        "grid": grid.to_strings(),
        "length": (path_length(path1), path_length(path2)),
        "time": (path_time(path1), path_time(path2)),
        "makespan": makespan(plan),
        "soc": sum_of_costs(plan),
        "sep_bad": min_separation(plan_bad),
        "sep": min_separation(plan),
        "sep_cont": min_separation_continuous(plan),
        "sep_per_t": [math.dist(position_at(path1, t), position_at(path2, t))
                      for t in range(4)],
    }
    # closest approach of two drones
    p_a, v_a = (0.0, 0.0), (1.0, 0.0)
    p_b, v_b = (4.0, 2.0), (0.0, -1.0)
    out["tca"] = time_of_closest_approach(p_a, v_a, p_b, v_b)
    out["ttc_r075"] = time_to_collision(p_a, v_a, 0.75, p_b, v_b, 0.75)
    out["ttc_r050"] = time_to_collision(p_a, v_a, 0.5, p_b, v_b, 0.5)
    # covariance ellipse
    sigma = np.array([[2.0, 1.2], [1.2, 1.0]])
    a, b, angle, _ = covariance_ellipse(sigma)
    out["ellipse"] = (a, b, math.degrees(angle))
    if verbose:
        print("Worked example of Chapter 2")
        for key, val in out.items():
            print(f"  {key:10s}: {val}")
    return out


# ---------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------
def _close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def _self_test():
    # --- grids -------------------------------------------------------
    g4 = Grid.from_strings(["....",
                            ".#..",
                            "...."], connectivity=4)
    assert g4.width == 4 and g4.height == 3
    assert (1, 1) in g4.obstacles and g4.to_strings() == ["....", ".#..", "...."]
    assert not g4.is_free((1, 1)) and not g4.is_free((-1, 0)) and g4.is_free((0, 0))
    assert sorted(c for c, _ in g4.neighbors((0, 0))) == [(0, 1), (1, 0)]
    assert sorted(c for c, _ in g4.neighbors((1, 0))) == [(0, 0), (2, 0)]
    assert all(_close(cost, 1.0) for _, cost in g4.neighbors((2, 1)))

    g8 = Grid.from_strings(["....",
                            ".#..",
                            "...."], connectivity=8)
    nb = dict(g8.neighbors((2, 1)))      # right of the obstacle
    # orthogonal: (3,1),(2,2),(2,0); diagonals (3,2),(3,0) allowed;
    # (1,2) and (1,0) would cut the corner of the obstacle (1,1)
    assert sorted(nb) == [(2, 0), (2, 2), (3, 0), (3, 1), (3, 2)]
    assert _close(nb[(3, 2)], SQRT2) and _close(nb[(3, 1)], 1.0)
    assert len(g8.neighbors((0, 0))) == 2          # corner next to the obstacle
    assert len(g8.neighbors((3, 0))) == 3          # free corner: 2 straight + 1 diagonal

    # --- inflation ---------------------------------------------------
    g = Grid(7, 7, obstacles=[(3, 3)])
    assert len(g.inflate(0.6).obstacles) == 5      # plus shape
    assert len(g.inflate(1.0).obstacles) == 9      # 3 x 3 block
    assert len(g.inflate(1.6).obstacles) == 21     # block plus a ring of 12
    assert (0, 3) not in g.inflate(1.6).obstacles and (1, 3) in g.inflate(1.6).obstacles
    assert g.inflate(1.0).connectivity == 4 and len(g.obstacles) == 1  # original untouched

    # --- edge counts and stretch factors ------------------------------
    e4, e8 = Grid(4, 3, connectivity=4), Grid(4, 3, connectivity=8)
    cells = [(x, y) for x in range(4) for y in range(3)]
    assert sum(len(e4.neighbors(c)) for c in cells) // 2 == 17    # 4*2 + 3*3
    assert sum(len(e8.neighbors(c)) for c in cells) // 2 == 29    # 17 + 2*3*2
    assert _close(lattice_stretch(2, diagonals=False), SQRT2)
    assert _close(lattice_stretch(3, diagonals=False), math.sqrt(3))
    assert _close(lattice_stretch(2), 1.0824, 1e-4)
    assert _close(lattice_stretch(3), 1.1281, 1e-4)
    th = math.radians(22.5)                          # worst direction in 2D
    assert _close(lattice_path_cost((math.cos(th), math.sin(th))), lattice_stretch(2))
    assert _close(lattice_path_cost((3, 2, 1)), 1 + SQRT2 + math.sqrt(3))
    assert lattice_path_cost((1, 1, 1)) / math.sqrt(3) <= lattice_stretch(3) + 1e-12

    # --- space-time --------------------------------------------------
    succ = space_time_successors(g4, ((0, 0), 0))
    assert ((0, 0), 1) in dict(succ) and len(succ) == 3
    assert all(t == 1 for (_, t), _ in succ)

    # --- plans and costs ---------------------------------------------
    ex = worked_example(verbose=False)
    assert ex["length"] == (3.0, 2.0)
    assert ex["time"] == (3, 3)
    assert ex["makespan"] == 3 and ex["soc"] == 6
    assert _close(ex["sep_bad"], 0.0)                # vertex collision at t = 1
    assert _close(ex["sep"], 1.0)
    assert _close(ex["sep_cont"], math.sqrt(0.5))    # 0.707 at t = 1.5
    assert path_time([(0, 0), (1, 0), (1, 0), (1, 0)]) == 1
    assert path_time([(0, 0), (1, 0), (0, 0), (1, 0), (1, 0)]) == 3
    assert makespan([[(0, 0)] * 4, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]]) == 5
    assert sum_of_costs([[(0, 0), (1, 0), (2, 0), (3, 0)],
                         [(5, 5), (5, 4), (5, 3), (5, 2), (5, 1), (5, 0)]]) == 8

    # --- geometry ----------------------------------------------------
    assert _close(dot((1, 2), (3, 4)), 11.0) and _close(cross((1, 0), (0, 1)), 1.0)
    d, q, s = point_segment_distance((1, 1), (0, 0), (2, 0))
    assert _close(d, 1.0) and q == (1.0, 0.0) and _close(s, 0.5)
    d, q, s = point_segment_distance((3, 1), (0, 0), (2, 0))
    assert _close(d, SQRT2) and q == (2.0, 0.0) and _close(s, 1.0)
    assert _close(point_segment_distance((5, 5), (1, 1), (1, 1))[0], math.sqrt(32))
    assert _close(ray_circle_intersection((0, 0), (1, 0), (3, 0), 1.0), 2.0)
    assert _close(ray_circle_intersection((0, 0), (2, 0), (3, 0), 1.0), 1.0)
    assert ray_circle_intersection((0, 0), (-1, 0), (3, 0), 1.0) is None
    assert ray_circle_intersection((0, 0), (1, 0), (3, 2), 1.0) is None
    assert _close(ray_circle_intersection((3, 0.5), (1, 0), (3, 0), 1.0), 0.0)
    assert segment_circle_intersects((0, 0), (5, 0), (2, 0.5), 1.0)
    assert not segment_circle_intersects((0, 0), (5, 0), (2, 1.5), 1.0)
    assert minkowski_disc((1, 1), 0.5, (2, 0), 0.25) == ((3, 1), 0.75)
    t1, t2 = tangent_points((0, 0), (4, 0), 2.0)
    assert _close(t1[0], 3.0) and _close(t1[1], -math.sqrt(3))   # (3, -sqrt 3)
    assert _close(t2[0], 3.0) and _close(t2[1], math.sqrt(3))    # (3, +sqrt 3)
    assert _close(norm(t1), math.sqrt(12))                       # tangent length
    assert tangent_points((3, 0), (4, 0), 2.0) is None
    t_star, d_min = time_of_closest_approach((0, 0), (1, 0), (4, 2), (0, -1))
    assert _close(t_star, 3.0) and _close(d_min, SQRT2)
    t_star, d_min = time_of_closest_approach((0, 0), (1, 0), (4, 2), (0, -1), horizon=2.0)
    assert _close(t_star, 2.0) and _close(d_min, 2.0)            # clamped to the horizon
    t_star, _ = time_of_closest_approach((0, 0), (0, 0), (4, 2), (1, 1))
    assert _close(t_star, 0.0)                                   # separating: now is closest
    assert _close(ex["tca"][0], 3.0) and _close(ex["tca"][1], SQRT2)
    assert _close(ex["ttc_r075"], (6.0 - math.sqrt(0.5)) / 2.0)   # 2.6464
    assert ex["ttc_r050"] is None

    # --- motion models -----------------------------------------------
    A, B = double_integrator_matrices(0.5, dim=1)
    assert np.allclose(A, [[1, 0.5], [0, 1]]) and np.allclose(B, [[0.125], [0.5]])
    x1 = double_integrator_step([0.0, 0.0], [1.0], 0.5)
    assert np.allclose(x1, [0.125, 0.5])
    assert np.allclose(x1, A @ np.array([0.0, 0.0]) + B @ np.array([1.0]))
    x2 = double_integrator_step([0.0, 0.0, 0.0, 0.0], [3.0, 4.0], 1.0, a_max=1.0)
    assert np.allclose(x2, [0.3, 0.4, 0.6, 0.8])                 # |u| clipped to 1
    x3 = double_integrator_step([0.0, 2.0], [1.0], 1.0, v_max=2.0)
    assert np.allclose(x3, [2.0, 2.0])                           # speed limit holds
    assert np.allclose(single_integrator_step([1.0, 1.0], [3.0, 4.0], 0.5, v_max=1.0),
                       [1.3, 1.4])
    assert _close(stopping_distance(4.0, 2.0), 4.0)
    assert _close(stopping_distance(2.0, 1.0), 2.0)

    # --- uncertainty -------------------------------------------------
    a, b, angle, _ = covariance_ellipse([[4.0, 0.0], [0.0, 1.0]])
    assert _close(a, 2.0) and _close(b, 1.0) and _close(abs(angle), 0.0)
    a, b, angle, _ = covariance_ellipse([[2.0, 1.0], [1.0, 2.0]], n_sigma=2.0)
    assert _close(a, 2 * math.sqrt(3)) and _close(b, 2.0)
    assert _close(math.degrees(angle), 45.0)
    a, b, angle, _ = covariance_ellipse([[2.0, 1.2], [1.2, 1.0]])
    assert _close(a, math.sqrt(2.8)) and _close(b, math.sqrt(0.2))
    assert _close(math.degrees(angle), math.degrees(math.atan2(2.0, 3.0)), 1e-6)  # 33.69 deg
    pts = ellipse_points([2.0, 1.0], [[2.0, 1.2], [1.2, 1.0]], n_sigma=1.0)
    assert all(_close(mahalanobis2(p, [2.0, 1.0], [[2.0, 1.2], [1.2, 1.0]]), 1.0)
               for p in pts)
    assert _close(gaussian_pdf([0.0, 0.0], [0.0, 0.0], np.eye(2)), 1.0 / (2 * math.pi))
    assert _close(mahalanobis2([1.0, 0.0], [0.0, 0.0], [[4.0, 0.0], [0.0, 1.0]]), 0.25)

    # --- lazy priority queue -----------------------------------------
    pq = LazyPQ()
    assert pq.push(5.0, "a") and pq.push(3.0, "b") and pq.push(4.0, "a")
    assert not pq.push(6.0, "a")                     # worse key: ignored
    assert len(pq) == 2 and "a" in pq and pq.peek_key() == 3.0
    assert pq.pop() == (3.0, "b") and pq.pop() == (4.0, "a")
    assert len(pq) == 0 and pq.stale_pops == 0       # (5.0, "a") still sits in the heap
    try:
        pq.pop()                                     # skips the stale entry, then fails
        raise AssertionError("expected IndexError")
    except IndexError:
        pass
    assert pq.stale_pops == 1
    pq.push(1.0, ((2, 3), 7))                        # hashable space-time states as items
    pq.push(1.0, ((0, 0), 7))
    assert pq.pop()[1] == ((2, 3), 7)                # equal keys: insertion order wins
    print("ch02_toolbox self-test passed")


if __name__ == "__main__":
    worked_example()
    _self_test()
