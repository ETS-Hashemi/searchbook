"""Dijkstra's algorithm -- reference implementation for Chapter 3.

Run this file to execute the self-test (it takes about a second):

    python3 code/ch03_dijkstra.py

The self-test compares dijkstra() with a brute-force enumeration of all
simple paths and with Bellman-Ford on random graphs, replays the
hand-worked example of the chapter (EXAMPLE_GRAPH) and checks every number
of its trace table, and exercises the grid adapter, path reconstruction,
the early exit, multi-source search, the backward (true-distance)
heuristic, the breadth-first special case and the negative-edge
counterexample.  The figure generators in code/figures/ import this file.
"""

import heapq
import math
import random
import time
from collections import deque

INF = float("inf")
SQRT2 = math.sqrt(2.0)


# ---------------------------------------------------------------------------
# The algorithm
# ---------------------------------------------------------------------------

def dijkstra(graph, source, target=None):
    """Shortest paths from source; every edge cost must be >= 0.

    graph[u] yields the (v, cost) pairs of the out-edges of u; a dict of
    lists or a GridGraph both work.  Returns (dist, parent): dist[v] is the
    cost of the best path found to v and parent[v] its predecessor on that
    path (parent[source] is None).  Unreached nodes are absent (infinity).
    With a target the loop stops as soon as the target is settled
    (uniform-cost search); dist is then exact for settled nodes only.
    """
    dist = {source: 0.0}
    parent = {source: None}
    closed = set()
    queue = [(0.0, source)]            # min-heap of (g, node) entries
    while queue:
        g, u = heapq.heappop(queue)    # smallest g first, ties by node
        if u in closed:                # stale entry: u was settled earlier
            continue
        closed.add(u)                  # settle u: dist[u] == g is final
        if u == target:
            break                      # early exit
        for v, cost in graph[u]:
            if v in closed:
                continue
            g_new = g + cost
            if g_new < dist.get(v, INF):
                dist[v] = g_new        # relaxation
                parent[v] = u
                heapq.heappush(queue, (g_new, v))   # lazy insertion
    return dist, parent


def reconstruct_path(parent, target):
    """Follow parent pointers back from target; None if unreachable."""
    if target not in parent:
        return None
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def path_cost(graph, path):
    """Sum of the edge costs along path (edges looked up in graph)."""
    total = 0.0
    for u, v in zip(path, path[1:]):
        total += min(c for w, c in graph[u] if w == v)
    return total


def dijkstra_trace(graph, source, target=None):
    """dijkstra() with a log of every step, for trace tables and figures.

    Each step is a dict: 'popped' = (g, node), 'stale' = True if the entry
    was discarded, 'relaxed' = [(v, g_new), ...] improvements made,
    'queue' = sorted queue after the step, 'closed' = settled nodes in the
    order in which they were settled.  The search logic is identical to
    dijkstra(); the self-test checks that both agree.
    """
    dist = {source: 0.0}
    parent = {source: None}
    closed = set()
    order = []
    queue = [(0.0, source)]
    steps = []
    while queue:
        g, u = heapq.heappop(queue)
        step = {"popped": (g, u), "stale": u in closed, "relaxed": []}
        if not step["stale"]:
            closed.add(u)
            order.append(u)
            if u != target:
                for v, cost in graph[u]:
                    if v in closed:
                        continue
                    g_new = g + cost
                    if g_new < dist.get(v, INF):
                        dist[v] = g_new
                        parent[v] = u
                        heapq.heappush(queue, (g_new, v))
                        step["relaxed"].append((v, g_new))
        step["queue"] = sorted(queue)
        step["closed"] = list(order)
        steps.append(step)
        if u == target and not step["stale"]:
            break
    return steps, dist, parent


# ---------------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------------

def multi_source_dijkstra(graph, sources, target=None):
    """Distance from every node to its nearest source.

    Identical to dijkstra() except that every source starts with g = 0
    (equivalently: a virtual source joined to all sources by 0-cost edges).
    """
    dist = {s: 0.0 for s in sources}
    parent = {s: None for s in sources}
    closed = set()
    queue = [(0.0, s) for s in sources]
    heapq.heapify(queue)
    while queue:
        g, u = heapq.heappop(queue)
        if u in closed:
            continue
        closed.add(u)
        if u == target:
            break
        for v, cost in graph[u]:
            if v in closed:
                continue
            g_new = g + cost
            if g_new < dist.get(v, INF):
                dist[v] = g_new
                parent[v] = u
                heapq.heappush(queue, (g_new, v))
    return dist, parent


def reverse_graph(graph):
    """Reverse every edge of a dict-of-lists graph."""
    rev = {u: [] for u in graph}
    for u, edges in graph.items():
        for v, cost in edges:
            rev.setdefault(v, []).append((u, cost))
    return rev


def backward_dijkstra_heuristic(graph, goal):
    """True-distance heuristic h*(v) = dist(v, goal) for every node v.

    One run of dijkstra() from the goal over the reversed graph.  The
    table is a perfect heuristic: admissible and consistent on the static
    map, and still admissible when wait actions or constraints are added
    (Chapters 4, 8 and 9).  Unreached nodes are absent: read as infinity.
    """
    if hasattr(graph, "reversed"):
        rev = graph.reversed()         # GridGraph knows how to flip itself
    else:
        rev = reverse_graph(graph)
    h_star, _ = dijkstra(rev, goal)
    return h_star


def bfs(graph, source):
    """Breadth-first search: Dijkstra when every edge costs the same."""
    dist = {source: 0}
    parent = {source: None}
    queue = deque([source])            # a FIFO queue replaces the heap
    while queue:
        u = queue.popleft()
        for v, _ in graph[u]:
            if v not in dist:          # first visit is the shortest one
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.append(v)
    return dist, parent


# ---------------------------------------------------------------------------
# Grid adapter
# ---------------------------------------------------------------------------

MOVES = {
    4: [(-1, 0), (0, -1), (0, 1), (1, 0)],
    8: [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
}


class GridGraph:
    """Presents a 2D occupancy grid to dijkstra() as a graph.

    cells[r][c] is 0 for a free cell and 1 for an obstacle; nodes are
    (row, col) tuples.  connectivity is 4 or 8; a diagonal move costs
    sqrt(2) and may not cut the corner of an obstacle.  cell_cost[r][c]
    (optional) multiplies the cost of every move that ENTERS cell (r, c),
    which makes the graph directed; reversed() flips all edges so that a
    backward search from the goal sees the correct costs.
    """

    def __init__(self, cells, connectivity=4, cell_cost=None, reverse=False):
        self.cells = [list(row) for row in cells]
        self.rows = len(self.cells)
        self.cols = len(self.cells[0])
        self.connectivity = connectivity
        self.cell_cost = cell_cost
        self.reverse = reverse

    def free(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and self.cells[r][c] == 0

    def nodes(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.cells[r][c] == 0]

    def reversed(self):
        return GridGraph(self.cells, self.connectivity, self.cell_cost,
                         not self.reverse)

    def __getitem__(self, node):
        r, c = node
        out = []
        for dr, dc in MOVES[self.connectivity]:
            r2, c2 = r + dr, c + dc
            if not self.free(r2, c2):
                continue
            if dr and dc and not (self.free(r + dr, c) and self.free(r, c + dc)):
                continue               # no corner cutting
            length = SQRT2 if dr and dc else 1.0
            entered = (r, c) if self.reverse else (r2, c2)
            mult = 1.0 if self.cell_cost is None else self.cell_cost[entered[0]][entered[1]]
            out.append(((r2, c2), length * mult))
        return out


def parse_grid(rows, slow_cost=3.0):
    """Read a picture of a grid: '#' obstacle, 'w' slow cell, S/T marks.

    Returns (GridGraph inputs) cells, cell_cost, start, goal.
    """
    cells, cost, start, goal = [], [], None, None
    for r, row in enumerate(rows):
        cells.append([1 if ch == "#" else 0 for ch in row])
        cost.append([slow_cost if ch == "w" else 1.0 for ch in row])
        for c, ch in enumerate(row):
            if ch == "S":
                start = (r, c)
            elif ch == "T":
                goal = (r, c)
    return cells, cost, start, goal


# ---------------------------------------------------------------------------
# Reference checkers (used only by the self-test)
# ---------------------------------------------------------------------------

def brute_force_distances(graph, source):
    """Enumerate every simple path from source (tiny graphs only)."""
    best = {source: 0.0}

    def extend(u, cost, visited):
        for v, c in graph[u]:
            if v in visited:
                continue
            if cost + c < best.get(v, INF):
                best[v] = cost + c
            extend(v, cost + c, visited | {v})

    extend(source, 0.0, {source})
    return best


def bellman_ford(graph, source):
    """Reference that tolerates negative edges (no negative cycles)."""
    nodes = set(graph)
    for u in graph:
        nodes.update(v for v, _ in graph[u])
    dist = {v: INF for v in nodes}
    dist[source] = 0.0
    for _ in range(len(nodes) - 1):
        for u in graph:
            for v, c in graph[u]:
                if dist[u] + c < dist[v]:
                    dist[v] = dist[u] + c
    return {v: d for v, d in dist.items() if d < INF}


# ---------------------------------------------------------------------------
# The examples of the chapter
# ---------------------------------------------------------------------------

def undirected(edge_costs):
    """Build a dict-of-lists graph from {(u, v): cost} with both directions."""
    graph = {}
    for (u, v), cost in edge_costs.items():
        graph.setdefault(u, []).append((v, float(cost)))
        graph.setdefault(v, []).append((u, float(cost)))
    for u in graph:
        graph[u].sort()
    return graph


# Waypoint graph of the worked example (Section "A worked example").
EXAMPLE_EDGES = {
    ("A", "B"): 2, ("A", "C"): 5, ("B", "C"): 1, ("B", "D"): 4,
    ("B", "E"): 7, ("C", "D"): 2, ("D", "E"): 3, ("D", "F"): 8,
    ("E", "F"): 4, ("E", "G"): 2, ("F", "G"): 1,
}
EXAMPLE_GRAPH = undirected(EXAMPLE_EDGES)
EXAMPLE_DIST = {"A": 0, "B": 2, "C": 3, "D": 5, "E": 8, "G": 10, "F": 11}
EXAMPLE_PATH = ["A", "B", "C", "D", "E", "G"]
# Expected pops (g, node, stale?) of dijkstra_trace(EXAMPLE_GRAPH, "A").
EXAMPLE_POPS = [
    (0, "A", False), (2, "B", False), (3, "C", False), (5, "C", True),
    (5, "D", False), (6, "D", True), (8, "E", False), (9, "E", True),
    (10, "G", False), (11, "F", False), (12, "F", True), (13, "F", True),
]

# 5 x 5 grid of the second example: free ring around a slow ring ('w',
# entering costs 3) with a blocked centre and a blocked cell on the right.
EXAMPLE_GRID = [
    "S....",
    ".www.",
    ".w#w#",
    ".www.",
    "....T",
]
EXAMPLE_GRID_COST = 8.0
EXAMPLE_GRID_PATH = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                     (4, 1), (4, 2), (4, 3), (4, 4)]
EXAMPLE_GRID_EXPANSIONS = 19       # settled cells when T is popped
EXAMPLE_GRID_FREE_CELLS = 23

# The negative-edge counterexample: dist(S, T) is 1 via S-B-A-T, but the
# algorithm settles A with g = 1 before B reveals the cheaper route.
NEGATIVE_EXAMPLE = {
    "S": [("A", 1.0), ("B", 2.0)],
    "A": [("T", 1.0)],
    "B": [("A", -2.0)],
    "T": [],
}


def random_graph(rng, n, m, directed=True, max_cost=9, float_costs=False):
    """Random graph with n nodes and about m edges, costs in [1, max_cost]."""
    graph = {i: [] for i in range(n)}
    for _ in range(m):
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        cost = rng.uniform(0.5, max_cost) if float_costs else float(rng.randint(1, max_cost))
        graph[u].append((v, cost))
        if not directed:
            graph[v].append((u, cost))
    return graph


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _format_entry(g, v):
    return "(%g,%s)" % (g, v if isinstance(v, str) else "%d%d" % v)


def print_trace(steps):
    """Print one line per step in the layout of the chapter's trace table."""
    for i, s in enumerate(steps, 1):
        g, u = s["popped"]
        if s["stale"]:
            action = "stale, discarded"
        elif s["relaxed"]:
            action = "relax " + " ".join(_format_entry(gn, v) for v, gn in s["relaxed"])
        else:
            action = "no improvement"
        queue = " ".join(_format_entry(g2, v2) for g2, v2 in s["queue"]) or "empty"
        print("%2d  pop %-8s %-32s queue: %s" % (i, _format_entry(g, u), action, queue))


def self_test():
    t0 = time.time()
    rng = random.Random(3)

    # 1. The worked example: distances, tree, trace, early exit.
    dist, parent = dijkstra(EXAMPLE_GRAPH, "A")
    assert dist == EXAMPLE_DIST, dist
    assert reconstruct_path(parent, "G") == EXAMPLE_PATH
    assert path_cost(EXAMPLE_GRAPH, EXAMPLE_PATH) == 10
    steps, tdist, tparent = dijkstra_trace(EXAMPLE_GRAPH, "A")
    assert tdist == dist and tparent == parent
    pops = [(s["popped"][0], s["popped"][1], s["stale"]) for s in steps]
    assert pops == EXAMPLE_POPS, pops
    assert sum(1 for s in steps if s["stale"]) == 5
    assert max(len(s["queue"]) for s in steps) == 4
    early, eparent = dijkstra(EXAMPLE_GRAPH, "A", target="G")
    assert early["G"] == 10 and reconstruct_path(eparent, "G") == EXAMPLE_PATH
    assert early["F"] == 12            # tentative only: F was not settled
    esteps, _, _ = dijkstra_trace(EXAMPLE_GRAPH, "A", target="G")
    assert len(esteps) == 9 and esteps[-1]["popped"] == (10, "G")
    # Exercise 1 of the chapter: the cost of edge B-E drops from 7 to 4.
    variant = undirected({**EXAMPLE_EDGES, ("B", "E"): 4})
    vdist, vparent = dijkstra(variant, "A")
    assert vdist == {"A": 0, "B": 2, "C": 3, "D": 5, "E": 6, "G": 8, "F": 9}
    assert reconstruct_path(vparent, "G") == ["A", "B", "E", "G"]
    vsteps, _, _ = dijkstra_trace(variant, "A")
    assert len(vsteps) == 11 and sum(s["stale"] for s in vsteps) == 4

    # 2. Random graphs against brute force and Bellman-Ford.
    for trial in range(300):
        n = rng.randint(2, 7)
        graph = random_graph(rng, n, rng.randint(1, 14), directed=rng.random() < 0.5,
                             float_costs=rng.random() < 0.5)
        dist, parent = dijkstra(graph, 0)
        ref = brute_force_distances(graph, 0)
        assert dist.keys() == ref.keys()
        for v in ref:
            assert abs(dist[v] - ref[v]) < 1e-9, (graph, v, dist[v], ref[v])
            path = reconstruct_path(parent, v)
            assert path[0] == 0 and path[-1] == v
            assert abs(path_cost(graph, path) - dist[v]) < 1e-9
        target = rng.randrange(n)
        edist, _ = dijkstra(graph, 0, target)
        assert (target in edist) == (target in ref)
        if target in ref:
            assert abs(edist[target] - ref[target]) < 1e-9
        # Every node that was settled before the target has a final value.
        for v, d in edist.items():
            if (d, v) <= (edist.get(target, INF), target):
                assert abs(d - ref[v]) < 1e-9
    for trial in range(20):
        graph = random_graph(rng, 40, 160, float_costs=True)
        dist, _ = dijkstra(graph, 0)
        ref = bellman_ford(graph, 0)
        assert dist.keys() == ref.keys()
        assert all(abs(dist[v] - ref[v]) < 1e-9 for v in ref)

    # 3. Multi-source search equals the minimum over single sources.
    for trial in range(30):
        graph = random_graph(rng, 12, 30)
        sources = rng.sample(range(12), 3)
        multi, _ = multi_source_dijkstra(graph, sources)
        singles = [dijkstra(graph, s)[0] for s in sources]
        for v in range(12):
            best = min(d.get(v, INF) for d in singles)
            assert multi.get(v, INF) == best

    # 4. Backward Dijkstra gives the true distance to the goal, and the
    #    table is consistent: h*(u) <= c(u, v) + h*(v) on every edge.
    for trial in range(30):
        graph = random_graph(rng, 10, 25, float_costs=True)
        goal = rng.randrange(10)
        h_star = backward_dijkstra_heuristic(graph, goal)
        for v in range(10):
            forward = dijkstra(graph, v, goal)[0].get(goal, INF)
            assert abs(h_star.get(v, INF) - forward) < 1e-9 or forward == INF == h_star.get(v, INF)
        for u in graph:
            for v, c in graph[u]:
                assert h_star.get(u, INF) <= c + h_star.get(v, INF) + 1e-9
    h_star = backward_dijkstra_heuristic(EXAMPLE_GRAPH, "G")
    assert h_star == {"G": 0, "F": 1, "E": 2, "D": 5, "C": 7, "B": 8, "A": 10}

    # 5. The grid example: cost, path, closed set, reversed grid.
    cells, cost, start, goal = parse_grid(EXAMPLE_GRID)
    grid = GridGraph(cells, 4, cost)
    assert len(grid.nodes()) == EXAMPLE_GRID_FREE_CELLS
    steps, gdist, gparent = dijkstra_trace(grid, start, goal)
    assert gdist[goal] == EXAMPLE_GRID_COST
    assert reconstruct_path(gparent, goal) == EXAMPLE_GRID_PATH
    assert len(steps[-1]["closed"]) == EXAMPLE_GRID_EXPANSIONS
    assert not any(s["stale"] for s in steps)   # no stale entries on this grid
    full, _ = dijkstra(grid, start)
    assert len(full) == EXAMPLE_GRID_FREE_CELLS and full[goal] == EXAMPLE_GRID_COST
    assert full[(3, 3)] == 10 and full[(1, 1)] == 4
    h_grid = backward_dijkstra_heuristic(grid, goal)
    assert h_grid[start] == EXAMPLE_GRID_COST and h_grid[(3, 3)] == 2
    # Entering a slow cell costs 3, leaving it costs 1: the graph is directed.
    assert full[(3, 2)] == 9 and h_grid[(3, 2)] == 3
    for v in grid.nodes():                       # h* equals a forward search
        assert dijkstra(grid, v, goal)[0][goal] == h_grid[v]

    # 6. Unit-cost 4-connected grids: BFS and Dijkstra agree; 8-connected
    #    diagonals cost sqrt(2) and corner cutting is forbidden.
    for trial in range(10):
        n = 12
        cells = [[1 if rng.random() < 0.25 else 0 for _ in range(n)] for _ in range(n)]
        cells[0][0] = 0
        g4 = GridGraph(cells, 4)
        d_bfs, _ = bfs(g4, (0, 0))
        d_dij, _ = dijkstra(g4, (0, 0))
        assert d_bfs.keys() == d_dij.keys()
        assert all(d_bfs[v] == d_dij[v] for v in d_bfs)
        g8 = GridGraph(cells, 8)
        d8, _ = dijkstra(g8, (0, 0))
        assert all(d8[v] <= d_dij[v] + 1e-9 for v in d_dij)
    corner = GridGraph([[0, 1], [0, 0]], 8)
    assert corner[(0, 0)] == [((1, 0), 1.0)]      # (1,1) needs a corner cut
    assert sorted(corner[(1, 0)]) == [((0, 0), 1.0), ((1, 1), 1.0)]
    assert ((1, 1), SQRT2) in GridGraph([[0, 0], [0, 0]], 8)[(0, 0)]

    # 7. A negative edge breaks the settled-node invariant.
    wrong, _ = dijkstra(NEGATIVE_EXAMPLE, "S")
    right = bellman_ford(NEGATIVE_EXAMPLE, "S")
    assert wrong["T"] == 2 and right["T"] == 1 and right["A"] == 0

    elapsed = time.time() - t0
    assert elapsed < 10, elapsed
    print("ch03_dijkstra: all self-tests passed (%.2f s)" % elapsed)


if __name__ == "__main__":
    self_test()
    print("\nTrace of the worked example (dijkstra_trace(EXAMPLE_GRAPH, 'A')):")
    steps, _, _ = dijkstra_trace(EXAMPLE_GRAPH, "A")
    print_trace(steps)
    print("\nBackward Dijkstra from G:", backward_dijkstra_heuristic(EXAMPLE_GRAPH, "G"))
    cells, cost, start, goal = parse_grid(EXAMPLE_GRID)
    steps, gdist, gparent = dijkstra_trace(GridGraph(cells, 4, cost), start, goal)
    print("\nGrid example: settled order (row,col)=g")
    print("  " + "  ".join("(%d,%d)=%g" % (r, c, gdist[(r, c)]) for r, c in steps[-1]["closed"]))
    print("  path:", reconstruct_path(gparent, goal), "cost", gdist[goal])
