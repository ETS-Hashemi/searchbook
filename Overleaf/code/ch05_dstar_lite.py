"""LPA* and D* Lite on 4-connected grids -- reference implementation for Chapter 5.

Run this file to execute the self-test (a few seconds):

    python3 code/ch05_dstar_lite.py

The self-test draws random 20x20 grids for many seeds, lets the robot walk
while random obstacles are inserted and removed, and checks after every
change that the path cost of D* Lite (and of LPA*) equals the cost that A*
computes from scratch, that the extracted path is valid, that the priority
queue holds exactly the locally inconsistent vertices, and that the first
search expands exactly as many vertices as A* with the same tie-breaking.
It also replays the two worked examples of the chapter.  Run with --examples to
print the traces and the LaTeX table rows used in the text.

Cells are (x, y) tuples with x the column (from the left) and y the row
(from the bottom), both 0-based, as in the figures.  Obstacles are kept as
vertices all of whose edges cost infinity, so the graph structure is fixed
and only edge costs change.
"""

import heapq
import random
import sys
import time
from collections import namedtuple

INF = float("inf")


# ---------------------------------------------------------------------------
# The grid world
# ---------------------------------------------------------------------------

def manhattan(a, b):
    """Manhattan distance; consistent on a 4-connected unit-cost grid."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Grid:
    """4-connected grid with unit costs; blocked cells have all edges at INF."""

    def __init__(self, width, height, blocked=()):
        self.width = width
        self.height = height
        self.blocked = set(blocked)

    def in_bounds(self, s):
        return 0 <= s[0] < self.width and 0 <= s[1] < self.height

    def neighbors(self, s):
        """All in-bounds 4-neighbours, blocked or not (Pred(s) = Succ(s))."""
        x, y = s
        return [n for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                if self.in_bounds(n)]

    def cost(self, u, v):
        """Edge cost c(u, v): 1 between free neighbours, INF otherwise."""
        if u in self.blocked or v in self.blocked:
            return INF
        return 1.0

    def set_blocked(self, cell, blocked=True):
        """Flip one cell; returns the cell so callers can collect changes."""
        if blocked:
            self.blocked.add(cell)
        else:
            self.blocked.discard(cell)
        return cell

    def cells(self):
        return [(x, y) for x in range(self.width) for y in range(self.height)]

    def free_cells(self):
        return [s for s in self.cells() if s not in self.blocked]


# ---------------------------------------------------------------------------
# Priority queue with lazy deletion
# ---------------------------------------------------------------------------

class PriorityQueue:
    """Min-heap of (key, vertex) entries with Remove by lazy deletion.

    key_of maps each queued vertex to its current key; a heap entry is live
    only if its key equals key_of[vertex], and stale entries are skipped
    when they surface.  Keys are tuples (lexicographic order); equal keys
    are ordered by the vertex so that traces are deterministic.
    """

    def __init__(self):
        self.heap = []
        self.key_of = {}

    def __contains__(self, s):
        return s in self.key_of

    def __len__(self):
        return len(self.key_of)

    def insert(self, s, key):
        self.key_of[s] = key
        heapq.heappush(self.heap, (key, s))

    def remove(self, s):
        del self.key_of[s]          # the heap entry becomes stale

    def _purge(self):
        while self.heap and self.key_of.get(self.heap[0][1]) != self.heap[0][0]:
            heapq.heappop(self.heap)

    def top_key(self):
        self._purge()
        return self.heap[0][0] if self.heap else (INF, INF)

    def pop(self):
        self._purge()
        key, s = heapq.heappop(self.heap)
        del self.key_of[s]
        return s


# ---------------------------------------------------------------------------
# LPA*: forward search from a fixed start (Koenig, Likhachev & Furcy 2004)
# ---------------------------------------------------------------------------

class LPAStar:
    """Lifelong Planning A* on a Grid; g-values are start distances."""

    def __init__(self, grid, start, goal, heuristic=manhattan):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.h = heuristic
        self.g = {}                  # missing entries are INF
        self.rhs = {start: 0.0}
        self.U = PriorityQueue()
        self.U.insert(start, (self.h(start, goal), 0.0))
        self.expansions = 0
        self.events = None           # list to record a trace, or None

    def g_of(self, s):
        return self.g.get(s, INF)

    def rhs_of(self, s):
        return self.rhs.get(s, INF)

    def _trace(self, *event):
        """Record an event for the worked examples (no-op unless enabled)."""
        if self.events is not None:
            self.events.append(event)

    def calculate_key(self, s):
        m = min(self.g_of(s), self.rhs_of(s))
        return (m + self.h(s, self.goal), m)

    def update_vertex(self, u):
        rhs_old, queued_old = self.rhs_of(u), u in self.U
        if u != self.start:
            self.rhs[u] = min(self.g_of(p) + self.grid.cost(p, u)
                              for p in self.grid.neighbors(u))
        if u in self.U:
            self.U.remove(u)
        if self.g_of(u) != self.rhs_of(u):
            self.U.insert(u, self.calculate_key(u))
        self._trace("update", u, rhs_old, self.rhs_of(u), queued_old,
                    u in self.U, self.U.key_of.get(u))

    def compute_shortest_path(self):
        """Repair the search; returns the number of vertex expansions."""
        n = 0
        while (self.U.top_key() < self.calculate_key(self.goal)
               or self.rhs_of(self.goal) != self.g_of(self.goal)):
            key = self.U.top_key()
            u = self.U.pop()
            n += 1
            if self.g_of(u) > self.rhs_of(u):           # overconsistent
                self.g[u] = self.rhs_of(u)
                self._trace("pop", u, key, "over", self.g[u])
                for s in self.grid.neighbors(u):
                    self.update_vertex(s)
            else:                                        # underconsistent
                self.g[u] = INF
                self._trace("pop", u, key, "under", INF)
                for s in self.grid.neighbors(u) + [u]:
                    self.update_vertex(s)
        self.expansions += n
        return n

    def notify_changed_cells(self, cells):
        """Cells whose blocked status flipped (the grid is already updated).

        Every directed edge touching such a cell changed; LPA* updates the
        head of each edge: the cell itself (edges into it) and each
        neighbour (edges out of it).
        """
        for b in cells:
            self.update_vertex(b)
            for v in self.grid.neighbors(b):
                self.update_vertex(v)

    def path(self):
        """Shortest path start -> goal, read backward from the goal."""
        if self.g_of(self.goal) == INF:
            return None
        path, s = [self.goal], self.goal
        while s != self.start:
            s = min(self.grid.neighbors(s),
                    key=lambda p: (self.g_of(p) + self.grid.cost(p, s), p))
            if self.g_of(s) == INF or len(path) > self.grid.width * self.grid.height:
                return None
            path.append(s)
        return path[::-1]


# ---------------------------------------------------------------------------
# D* Lite, final version (Koenig & Likhachev 2002)
# ---------------------------------------------------------------------------

class DStarLite:
    """D* Lite on a Grid; g-values are goal distances, the start may move."""

    def __init__(self, grid, start, goal, heuristic=manhattan):
        self.grid = grid
        self.start = start           # the robot's current cell
        self.goal = goal
        self.h = heuristic
        self.k_m = 0.0
        self.s_last = start
        self.g = {}
        self.rhs = {goal: 0.0}
        self.U = PriorityQueue()
        self.U.insert(goal, (self.h(start, goal), 0.0))
        self.expansions = 0
        self.events = None

    def g_of(self, s):
        return self.g.get(s, INF)

    def rhs_of(self, s):
        return self.rhs.get(s, INF)

    def _trace(self, *event):
        """Record an event for the worked examples (no-op unless enabled)."""
        if self.events is not None:
            self.events.append(event)

    def calculate_key(self, s):
        m = min(self.g_of(s), self.rhs_of(s))
        return (m + self.h(self.start, s) + self.k_m, m)

    def update_vertex(self, u):
        rhs_old, queued_old = self.rhs_of(u), u in self.U
        if u != self.goal:
            self.rhs[u] = min(self.grid.cost(u, s) + self.g_of(s)
                              for s in self.grid.neighbors(u))
        if u in self.U:
            self.U.remove(u)
        if self.g_of(u) != self.rhs_of(u):
            self.U.insert(u, self.calculate_key(u))
        self._trace("update", u, rhs_old, self.rhs_of(u), queued_old,
                    u in self.U, self.U.key_of.get(u))

    def compute_shortest_path(self):
        """Repair the search; returns the number of vertex expansions."""
        n = 0
        while (self.U.top_key() < self.calculate_key(self.start)
               or self.rhs_of(self.start) != self.g_of(self.start)):
            k_old = self.U.top_key()
            u = self.U.pop()
            k_new = self.calculate_key(u)
            if k_old < k_new:                            # stale lower bound
                self.U.insert(u, k_new)
                self._trace("reinsert", u, k_old, k_new)
            elif self.g_of(u) > self.rhs_of(u):          # overconsistent
                self.g[u] = self.rhs_of(u)
                n += 1
                self._trace("pop", u, k_old, "over", self.g[u])
                for s in self.grid.neighbors(u):
                    self.update_vertex(s)
            else:                                        # underconsistent
                self.g[u] = INF
                n += 1
                self._trace("pop", u, k_old, "under", INF)
                for s in self.grid.neighbors(u) + [u]:
                    self.update_vertex(s)
        self.expansions += n
        return n

    def next_step(self):
        """Successor of the robot's cell minimising c + g; None if no path."""
        if self.g_of(self.start) == INF:
            return None
        return min(self.grid.neighbors(self.start),
                   key=lambda s: (self.grid.cost(self.start, s) + self.g_of(s), s))

    def move(self):
        """Move the robot one step along the current plan (lines 26'-27')."""
        s = self.next_step()
        if s is not None:
            self.start = s
        return s

    def notify_changed_cells(self, cells, replan=True):
        """Lines 28'-35': process cells whose blocked status flipped.

        Adds h(s_last, s_start) to k_m, updates the tail of every changed
        edge (the cell and each neighbour) and, if replan, repairs the
        search.  Returns the number of expansions.
        """
        if not cells:
            return 0
        self.k_m += self.h(self.s_last, self.start)
        self.s_last = self.start
        for b in cells:
            self.update_vertex(b)
            for u in self.grid.neighbors(b):
                self.update_vertex(u)
        return self.compute_shortest_path() if replan else 0

    def path(self):
        """The route the robot will follow: forward from start over Succ."""
        if self.g_of(self.start) == INF:
            return None
        path, s = [self.start], self.start
        while s != self.goal:
            s = min(self.grid.neighbors(s),
                    key=lambda t: (self.grid.cost(s, t) + self.g_of(t), t))
            if self.g_of(s) == INF or len(path) > self.grid.width * self.grid.height:
                return None
            path.append(s)
        return path


# ---------------------------------------------------------------------------
# A* from scratch (baseline)
# ---------------------------------------------------------------------------

AStarResult = namedtuple("AStarResult", "cost path expansions closed")


def astar(grid, start, goal, heuristic=manhattan, tie="h"):
    """Plain A* with a closed set.

    Ties on f are broken toward smaller h (tie="h", the usual choice on
    grids) or toward smaller g (tie="g", the order of the LPA*/D* Lite key).
    """
    g = {start: 0.0}
    parent = {start: None}
    closed = set()
    h0 = heuristic(start, goal)
    frontier = [(h0, 0.0 if tie == "g" else h0, start)]
    expansions = 0
    while frontier:
        _, _, u = heapq.heappop(frontier)
        if u in closed:
            continue
        closed.add(u)
        expansions += 1
        if u == goal:
            path, s = [], u
            while s is not None:
                path.append(s)
                s = parent[s]
            return AStarResult(g[u], path[::-1], expansions, closed)
        for v in grid.neighbors(u):
            c = grid.cost(u, v)
            if c == INF or v in closed:
                continue
            if g[u] + c < g.get(v, INF):
                g[v] = g[u] + c
                parent[v] = u
                hv = heuristic(v, goal)
                heapq.heappush(frontier, (g[v] + hv, g[v] if tie == "g" else hv, v))
    return AStarResult(INF, None, expansions, closed)


def reachable(grid, start, goal):
    """Breadth-first reachability test (used by the drivers)."""
    seen, queue = {start}, [start]
    while queue:
        u = queue.pop()
        if u == goal:
            return True
        for v in grid.neighbors(u):
            if v not in seen and grid.cost(u, v) < INF:
                seen.add(v)
                queue.append(v)
    return False


# ---------------------------------------------------------------------------
# Worked examples of the chapter
# ---------------------------------------------------------------------------

def fmt(x):
    return "\\infty" if x == INF else "%g" % x


def fmt_cell(s):
    return "$(%d,%d)$" % s


def fmt_key(k):
    return "$[%s;%s]$" % (fmt(k[0]), fmt(k[1]))


def latex_trace(events):
    """Turn a list of trace events into LaTeX table rows (one per pop or reinsert)."""
    rows, step, current = [], 0, None
    for ev in events:
        if ev[0] == "pop":
            if current is not None:
                rows.append(current)
            step += 1
            _, u, key, case, g_after = ev
            current = [step, "%s %s" % (fmt_cell(u), fmt_key(key)), case, "$%s$" % fmt(g_after), []]
        elif ev[0] == "update" and current is not None:
            _, s, rhs_old, rhs_new, q_old, q_new, key = ev
            if rhs_old == rhs_new and q_old == q_new:
                continue
            if q_new:
                current[4].append("%s: $%s$, %s" % (fmt_cell(s), fmt(rhs_new), fmt_key(key)))
            elif q_old:
                current[4].append("%s: $%s$, out" % (fmt_cell(s), fmt(rhs_new)))
            else:
                current[4].append("%s: $%s$" % (fmt_cell(s), fmt(rhs_new)))
        elif ev[0] == "reinsert":
            if current is not None:
                rows.append(current)
            step += 1
            _, u, k_old, k_new = ev
            current = [step, "%s %s" % (fmt_cell(u), fmt_key(k_old)), "reinsert", "--",
                       ["new key %s" % fmt_key(k_new)]]
    if current is not None:
        rows.append(current)
    lines = []
    for r in rows:
        upd = "; ".join(r[4]) if r[4] else "--"
        lines.append("  %d & %s & %s & %s & %s\\\\" % (r[0], r[1], r[2], r[3], upd))
    return lines


def snapshot(planner):
    """Copy of g, rhs and queue membership of a planner."""
    cells = planner.grid.cells()
    return {"g": {s: planner.g_of(s) for s in cells},
            "rhs": {s: planner.rhs_of(s) for s in cells},
            "queue": set(planner.U.key_of)}


LPA_EXAMPLE = {"width": 5, "height": 3, "start": (0, 1), "goal": (4, 1),
               "blocked": (), "new_obstacle": (3, 1)}


def lpastar_example(verbose=False):
    """Example 5.x: LPA* on the 5x3 grid, then cell (3,1) becomes blocked."""
    e = LPA_EXAMPLE
    grid = Grid(e["width"], e["height"], e["blocked"])
    lpa = LPAStar(grid, e["start"], e["goal"])
    lpa.events = []
    n_first = lpa.compute_shortest_path()
    first_events = lpa.events
    state_first = snapshot(lpa)
    path_first = lpa.path()
    grid.set_blocked(e["new_obstacle"])
    lpa.events = []
    lpa.notify_changed_cells([e["new_obstacle"]])
    change_events = lpa.events
    state_change = snapshot(lpa)
    lpa.events = []
    n_repair = lpa.compute_shortest_path()
    repair_events = lpa.events
    state_repair = snapshot(lpa)
    path_repair = lpa.path()
    a_after = astar(grid, e["start"], e["goal"])
    result = {"grid": grid, "n_first": n_first, "n_repair": n_repair,
              "path_first": path_first, "path_repair": path_repair,
              "state_first": state_first, "state_change": state_change,
              "state_repair": state_repair, "astar_after": a_after,
              "first_rows": latex_trace(first_events),
              "repair_rows": latex_trace(repair_events),
              "change_events": change_events}
    if verbose:
        print("LPA* example: first search %d expansions, path %s cost %g"
              % (n_first, path_first, len(path_first) - 1))
        print("\n".join(result["first_rows"]))
        print("changed edges -> UpdateVertex:")
        for ev in change_events:
            _, s, r0, r1, q0, q1, key = ev
            print("  %s rhs %s -> %s queued %s -> %s key %s" % (s, fmt(r0), fmt(r1), q0, q1, key))
        print("repair: %d expansions, path %s cost %g; A* from scratch: %d expansions cost %g"
              % (n_repair, path_repair, len(path_repair) - 1, a_after.expansions, a_after.cost))
        print("\n".join(result["repair_rows"]))
    return result


DSL_EXAMPLE = {"width": 7, "height": 5, "start": (0, 3), "goal": (6, 2),
               "blocked": ((3, 0), (3, 1), (3, 2)), "steps_before": 2,
               "new_obstacle": (3, 3)}


def dstar_lite_example(verbose=False):
    """Example 5.x: D* Lite, robot walks two steps, then (3,3) is blocked."""
    e = DSL_EXAMPLE
    grid = Grid(e["width"], e["height"], e["blocked"])
    d = DStarLite(grid, e["start"], e["goal"])
    d.events = []
    n0 = d.compute_shortest_path()
    init_events = d.events
    key_start = d.calculate_key(d.start)
    state0 = snapshot(d)
    path0 = d.path()
    trace = [(0, d.start, "initial search", d.k_m, 0, n0, d.g_of(d.start))]
    route = [d.start]
    t = 0
    for _ in range(e["steps_before"]):
        t += 1
        d.move()
        route.append(d.start)
        trace.append((t, d.start, "move, no change", d.k_m, 0, 0, d.g_of(d.start)))
    g_obstacle = d.g_of(e["new_obstacle"])
    grid.set_blocked(e["new_obstacle"])
    d.events = []
    d.notify_changed_cells([e["new_obstacle"]], replan=False)
    change_events = d.events
    inconsistent = {ev[1] for ev in change_events if ev[5]}
    n_updated = sum(1 for ev in change_events
                    if ev[2] != ev[3] or ev[4] != ev[5])
    state_change = snapshot(d)
    d.events = []
    n1 = d.compute_shortest_path()
    repair_events = d.events
    expanded = [ev[1] for ev in repair_events if ev[0] == "pop"]
    reinserted = [ev[1] for ev in repair_events if ev[0] == "reinsert"]
    state1 = snapshot(d)
    path1 = d.path()
    trace.append((t, d.start, "cell %s blocked, repair" % (e["new_obstacle"],),
                  d.k_m, n_updated, n1, d.g_of(d.start)))
    a_after = astar(grid, d.start, d.goal)
    robot_after_change = d.start
    while d.start != d.goal:
        t += 1
        d.move()
        route.append(d.start)
    trace.append((t, d.start, "goal reached", d.k_m, 0, 0, d.g_of(d.start)))
    result = {"grid": grid, "n0": n0, "n1": n1, "key_start": key_start,
              "state0": state0, "state_change": state_change, "state1": state1,
              "path0": path0, "path1": path1, "route": route, "trace": trace,
              "inconsistent": inconsistent, "expanded": expanded,
              "reinserted": reinserted, "g_obstacle": g_obstacle,
              "robot_after_change": robot_after_change, "astar_after": a_after,
              "change_events": change_events, "init_rows": latex_trace(init_events),
              "repair_rows": latex_trace(repair_events)}
    if verbose:
        print("D* Lite example: initial search %d expansions, key(start)=%s, path %s cost %g"
              % (n0, key_start, path0, len(path0) - 1))
        for row in trace:
            print("  t=%d robot=%s %-28s k_m=%g updated=%d exp=%d g(start)=%s"
                  % (row[0], row[1], row[2], row[3], row[4], row[5], fmt(row[6])))
        print("g(obstacle cell) before change:", fmt(g_obstacle))
        print("UpdateVertex after the change:")
        for ev in change_events:
            _, s, r0, r1, q0, q1, key = ev
            print("  %s rhs %s -> %s queued %s -> %s key %s" % (s, fmt(r0), fmt(r1), q0, q1, key))
        print("repair expanded (in order):", expanded)
        print("reinserted without expansion:", reinserted)
        print("\n".join(result["repair_rows"]))
        print("new path:", path1, "cost", len(path1) - 1)
        print("A* from %s on the changed grid: %d expansions, cost %g"
              % (robot_after_change, a_after.expansions, a_after.cost))
        print("robot route:", route)
    return result


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def check_path(grid, path, cost):
    assert path is not None and len(path) - 1 == cost, (path, cost)
    for u, v in zip(path, path[1:]):
        assert v in grid.neighbors(u) and grid.cost(u, v) == 1.0, (u, v)


def check_queue_invariant(planner):
    """U contains exactly the inconsistent vertices; keys are lower bounds.

    For D* Lite the second part holds right after ComputeShortestPath, when
    k_m accounts for every move of the robot so far (line 37'' of Main).
    """
    for s in planner.grid.cells():
        inconsistent = planner.g_of(s) != planner.rhs_of(s)
        assert inconsistent == (s in planner.U), s
        if s in planner.U:
            assert planner.U.key_of[s] <= planner.calculate_key(s), s


def random_walk_test(seed, size=20, density=0.25, steps=20):
    rng = random.Random(seed)
    cells = [(x, y) for x in range(size) for y in range(size)]
    blocked = {s for s in cells if rng.random() < density}
    free = [s for s in cells if s not in blocked]
    start, goal = rng.sample(free, 2)
    grid = Grid(size, size, blocked)
    dsl = DStarLite(grid, start, goal)
    dsl.compute_shortest_path()
    lpa = LPAStar(grid, start, goal)
    lpa.compute_shortest_path()
    ref = astar(grid, start, goal)
    assert dsl.g_of(start) == ref.cost == lpa.g_of(goal)
    # The first search is A* with the same tie-breaking, expansion for
    # expansion: backward from the goal for D* Lite, forward for LPA*.
    assert dsl.expansions == astar(grid, goal, start, tie="g").expansions, seed
    assert lpa.expansions == astar(grid, start, goal, tie="g").expansions, seed
    for _ in range(steps):
        if dsl.start != goal and dsl.next_step() is not None:
            dsl.move()
        changed = []
        for _ in range(rng.randint(1, 3)):
            c = rng.choice(cells)
            if c in (dsl.start, goal, start) or c in changed:
                continue
            grid.set_blocked(c, c not in grid.blocked)
            changed.append(c)
        dsl.notify_changed_cells(changed)
        lpa.notify_changed_cells(changed)
        lpa.compute_shortest_path()
        if changed:                       # k_m is up to date after a repair
            check_queue_invariant(dsl)
        check_queue_invariant(lpa)
        ref = astar(grid, dsl.start, goal)
        assert dsl.g_of(dsl.start) == ref.cost, (seed, dsl.start, dsl.g_of(dsl.start), ref.cost)
        if ref.cost < INF:
            check_path(grid, dsl.path(), ref.cost)
        ref_lpa = astar(grid, start, goal)
        assert lpa.g_of(goal) == ref_lpa.cost, (seed, lpa.g_of(goal), ref_lpa.cost)
        if ref_lpa.cost < INF:
            check_path(grid, lpa.path(), ref_lpa.cost)
    assert dsl.k_m >= 0


def self_test():
    t0 = time.perf_counter()
    # Priority queue.
    q = PriorityQueue()
    q.insert("a", (3, 1))
    q.insert("b", (2, 5))
    q.insert("c", (2, 4))
    assert q.top_key() == (2, 4) and q.pop() == "c"
    q.remove("b")
    assert q.top_key() == (3, 1) and "b" not in q and len(q) == 1
    q.insert("a", (1, 0))
    assert q.pop() == "a" and q.top_key() == (INF, INF)
    # Worked examples.
    lpa = lpastar_example()
    assert lpa["n_first"] == 5 and len(lpa["path_first"]) - 1 == 4
    assert len(lpa["path_repair"]) - 1 == 6 == lpa["astar_after"].cost
    dsl = dstar_lite_example()
    assert len(dsl["path0"]) - 1 == 7 and dsl["trace"][-1][1] == DSL_EXAMPLE["goal"]
    assert dsl["trace"][3][3] == 2.0                       # k_m after two steps
    assert len(dsl["path1"]) - 1 == dsl["astar_after"].cost
    assert (3, 3) not in dsl["route"]
    # Random walks with obstacle insertions and removals.
    for seed in range(30):
        random_walk_test(seed)
    print("self-test passed in %.1f s" % (time.perf_counter() - t0))


if __name__ == "__main__":
    if "--examples" in sys.argv:
        lpastar_example(verbose=True)
        print()
        dstar_lite_example(verbose=True)
    else:
        self_test()
