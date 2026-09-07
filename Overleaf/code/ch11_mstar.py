#!/usr/bin/env python3
"""Joint-space A*, independence detection, M* and push-and-swap primitives.

Reference implementation for Chapter 11 of "Multi-Agent Path Planning and
Drone Collision Avoidance".

Conventions
-----------
* A map is a list of strings, one per row, written top row first as in a
  picture: '.' is free, '@' is blocked.  A cell is a tuple ``(x, y)`` with
  ``x`` the column and ``y`` the row, ``(0, 0)`` in the bottom-left corner as
  in the figures of the book (Chapters 2 and 4).
* A joint configuration is a tuple of cells, one per agent.  A joint path is
  a list of configurations; ``path[t][i]`` is where agent ``i`` is at time t.
* One joint step costs the number of agents that are not resting at their
  goal: a move costs 1, a wait away from the goal costs 1, a wait at the goal
  costs 0 (the convention of Standley 2010 and Wagner and Choset 2011).
* Two agents conflict when they occupy the same cell (vertex conflict) or
  exchange cells along an edge (swap conflict); following is allowed, as in
  Chapter 7.
* Abstract graphs (for the push-and-swap primitives) use string vertex names.

Run ``python3 ch11_mstar.py`` for the self-test (a few seconds).
"""
from __future__ import annotations

import heapq
import itertools
import random
import time
from collections import deque
from dataclasses import dataclass, field

INF = float("inf")


# ---------------------------------------------------------------------------
# Graphs and instances
# ---------------------------------------------------------------------------
class Graph:
    """An undirected graph given by adjacency lists (insertion order kept)."""

    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v):
        self.adj.setdefault(u, [])
        self.adj.setdefault(v, [])
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)

    def add_vertex(self, u):
        self.adj.setdefault(u, [])

    @property
    def vertices(self):
        return list(self.adj)

    def neighbours(self, u):
        return self.adj[u]

    def degree(self, u):
        return len(self.adj[u])

    @classmethod
    def from_edges(cls, edges):
        g = cls()
        for u, v in edges:
            g.add_edge(u, v)
        return g

    @classmethod
    def from_map(cls, rows):
        """4-connected grid graph of a map; neighbour order E, W, N, S."""
        height = len(rows)
        width = len(rows[0])
        free = {(x, height - 1 - r) for r, row in enumerate(rows)
                for x, ch in enumerate(row) if ch == "."}
        g = cls()
        for cell in sorted(free):
            g.add_vertex(cell)
        for (x, y) in sorted(free):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (x + dx, y + dy)
                if nb in free:
                    g.adj[(x, y)].append(nb)
        return g


def bfs_distances(graph, source):
    """Unit-cost distances from ``source`` to every reachable vertex."""
    dist = {source: 0}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in graph.neighbours(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def bfs_path(graph, source, target, avoid=frozenset()):
    """A shortest path (list of vertices) avoiding ``avoid``, or None."""
    if source == target:
        return [source]
    parent = {source: None}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in graph.neighbours(u):
            if v in parent or v in avoid:
                continue
            parent[v] = u
            if v == target:
                path = [v]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                return path[::-1]
            queue.append(v)
    return None


@dataclass
class MAPFInstance:
    """A graph plus k agents with distinct starts and goals."""
    graph: Graph
    starts: list
    goals: list
    name: str = "instance"

    @property
    def k(self):
        return len(self.starts)

    def sub_instance(self, agents):
        return MAPFInstance(self.graph, [self.starts[i] for i in agents],
                            [self.goals[i] for i in agents], self.name)


# ---------------------------------------------------------------------------
# Individual policies, joint costs and collisions
# ---------------------------------------------------------------------------
class Policies:
    """Optimal individual policies: distance tables and next-step rules.

    ``dist[i][v]`` is the shortest-path distance of agent i from v to its
    goal; ``step(i, v)`` moves agent i one step closer (ties broken by the
    neighbour order of the graph) and returns v itself at the goal.
    """

    def __init__(self, inst):
        self.inst = inst
        self.dist = [bfs_distances(inst.graph, g) for g in inst.goals]
        self._next = [{} for _ in inst.goals]

    def step(self, i, v):
        nxt = self._next[i].get(v)
        if nxt is None:
            d = self.dist[i]
            if d.get(v, INF) == 0:
                nxt = v
            else:
                nxt = v
                for u in self.inst.graph.neighbours(v):
                    if d.get(u, INF) == d[v] - 1:
                        nxt = u
                        break
            self._next[i][v] = nxt
        return nxt

    def h(self, config):
        """Sum of the individual distances: admissible and consistent."""
        return sum(self.dist[i].get(v, INF) for i, v in enumerate(config))


def step_cost(config, nxt, goals):
    """Number of agents that are not resting at their goal during the step."""
    return sum(1 for i in range(len(config))
               if not (config[i] == goals[i] and nxt[i] == goals[i]))


def vertex_collisions(nxt):
    """Agents that occupy the same cell in the configuration ``nxt``."""
    bad = set()
    where = {}
    for i, v in enumerate(nxt):
        if v in where:
            bad.add(i)
            bad.add(where[v])
        else:
            where[v] = i
    return bad


def collisions(config, nxt):
    """Agents in a vertex or swap collision when moving config -> nxt."""
    bad = vertex_collisions(nxt)
    where = {v: i for i, v in enumerate(nxt)}
    for i in range(len(config)):
        j = where.get(config[i])            # who arrives where i was
        if j is not None and j != i and nxt[i] == config[j]:
            bad.add(i)
            bad.add(j)
    return bad


def agent_moves(graph, v):
    """Wait first, then the neighbours (the wait keeps the order stable)."""
    return [v] + list(graph.neighbours(v))


# ---------------------------------------------------------------------------
# Result container and plan utilities
# ---------------------------------------------------------------------------
@dataclass
class Result:
    """Outcome of a multi-agent search."""
    path: list = None                 # joint path or None
    cost: float = INF
    expansions: int = 0
    generated: int = 0
    seconds: float = 0.0
    info: dict = field(default_factory=dict)

    @property
    def solved(self):
        return self.path is not None


def paths_from_joint(joint_path):
    """Split a joint path into one path per agent."""
    k = len(joint_path[0])
    return [[cfg[i] for cfg in joint_path] for i in range(k)]


def joint_from_paths(paths):
    """Combine per-agent paths (padded by staying at the last cell)."""
    horizon = max(len(p) for p in paths)
    return [tuple(p[min(t, len(p) - 1)] for p in paths) for t in range(horizon)]


def active_cost(paths, goals):
    """The chapter's joint cost: steps in which an agent is not resting at its goal."""
    joint = joint_from_paths(paths)
    return sum(step_cost(joint[t], joint[t + 1], goals) for t in range(len(joint) - 1))


def sum_of_costs(paths, goals):
    """Chapter 7 objective: time of the final arrival at the goal, per agent."""
    total = 0
    for p, g in zip(paths, goals):
        t = len(p) - 1
        while t > 0 and p[t - 1] == g and p[t] == g:
            t -= 1
        total += t
    return total


def makespan(paths):
    return max(len(p) for p in paths) - 1


def validate(paths, inst):
    """True iff every path is legal and the plan has no vertex/swap conflict."""
    for i, p in enumerate(paths):
        if p[0] != inst.starts[i] or p[-1] != inst.goals[i]:
            return False
        for a, b in zip(p, p[1:]):
            if a != b and b not in inst.graph.neighbours(a):
                return False
    joint = joint_from_paths(paths)
    return all(not collisions(joint[t], joint[t + 1]) for t in range(len(joint) - 1))


def plans_conflict(paths_a, paths_b):
    """First conflict between two groups' plans (i, j, t) or None."""
    ja, jb = joint_from_paths(paths_a), joint_from_paths(paths_b)
    horizon = max(len(ja), len(jb))
    for t in range(horizon):
        ca = ja[min(t, len(ja) - 1)]
        cb = jb[min(t, len(jb) - 1)]
        na = ja[min(t + 1, len(ja) - 1)]
        nb = jb[min(t + 1, len(jb) - 1)]
        for i, va in enumerate(ca):
            for j, vb in enumerate(cb):
                if va == vb:
                    return (i, j, t)
                if t + 1 < horizon and na[i] == vb and nb[j] == va:
                    return (i, j, t)
    return None


# ---------------------------------------------------------------------------
# Joint-space A* (with optional operator decomposition)
# ---------------------------------------------------------------------------
def joint_astar(inst, operator_decomposition=False, max_generated=None):
    """A* in the joint configuration space with h = sum of distances.

    With ``operator_decomposition`` the agents choose their moves one after
    another through intermediate states (Standley 2010), so that a node has
    at most b + 1 successors instead of (b + 1)^k.
    """
    t0 = time.perf_counter()
    pol = Policies(inst)
    start, goal = tuple(inst.starts), tuple(inst.goals)
    goals = inst.goals
    if pol.h(start) == INF:
        return Result(None, INF, 0, 0, time.perf_counter() - t0)
    counter = itertools.count()
    stats = {"generated": 0}                  # candidates before the collision check
    if not operator_decomposition:
        def successors(cfg):
            for nxt in itertools.product(*[agent_moves(inst.graph, v) for v in cfg]):
                stats["generated"] += 1
                if not collisions(cfg, nxt):
                    yield nxt, step_cost(cfg, nxt, goals)
        h = lambda s: pol.h(s)                # noqa: E731
        is_goal = lambda s: s == goal         # noqa: E731
    else:
        # state = (config, partial next config); partial has i entries
        def successors(state):
            cfg, part = state
            i = len(part)
            for v in agent_moves(inst.graph, cfg[i]):
                stats["generated"] += 1
                if v in part:
                    continue                  # vertex collision with an assigned agent
                if any(v == cfg[j] and part[j] == cfg[i] for j in range(i)):
                    continue                  # swap with an assigned agent
                c = 0 if (cfg[i] == goals[i] and v == goals[i]) else 1
                new_part = part + (v,)
                if i + 1 == len(cfg):
                    yield (new_part, ()), c
                else:
                    yield (cfg, new_part), c

        def h(state):
            cfg, part = state
            return sum(pol.dist[i][part[i] if i < len(part) else cfg[i]]
                       for i in range(len(cfg)))
        is_goal = lambda s: s[0] == goal and s[1] == ()   # noqa: E731
        start = (start, ())
    g = {start: 0}
    parent = {start: None}
    open_heap = [(h(start), 0, next(counter), start)]
    expansions = 0
    while open_heap:
        f, neg_g, _, s = heapq.heappop(open_heap)
        if -neg_g > g[s]:
            continue                          # stale entry
        if is_goal(s):
            cost = g[s]
            path = []
            while s is not None:
                if not operator_decomposition or s[1] == ():
                    path.append(s if not operator_decomposition else s[0])
                s = parent[s]
            return Result(path[::-1], cost, expansions, stats["generated"],
                          time.perf_counter() - t0)
        expansions += 1
        for nxt, c in successors(s):
            new_g = g[s] + c
            if new_g < g.get(nxt, INF):
                g[nxt] = new_g
                parent[nxt] = s
                heapq.heappush(open_heap, (new_g + h(nxt), -new_g, next(counter), nxt))
        if max_generated is not None and stats["generated"] > max_generated:
            return Result(None, INF, expansions, stats["generated"],
                          time.perf_counter() - t0, {"aborted": True})
    return Result(None, INF, expansions, stats["generated"], time.perf_counter() - t0)


# ---------------------------------------------------------------------------
# Independence detection (Standley 2010, simple version)
# ---------------------------------------------------------------------------
def independence_detection(inst, solver=None, max_generated=None):
    """Plan groups independently and merge two groups only if they conflict.

    ``solver(sub_instance)`` must return a Result with an optimal joint path;
    the default is joint A*.  The returned Result carries the final groups.
    """
    t0 = time.perf_counter()
    solve = solver or (lambda sub: joint_astar(sub, max_generated=max_generated))
    groups = [[i] for i in range(inst.k)]
    plans = {}
    expansions = generated = 0
    for gi, grp in enumerate(groups):
        r = solve(inst.sub_instance(grp))
        expansions += r.expansions
        generated += r.generated
        if not r.solved:
            return Result(None, INF, expansions, generated, time.perf_counter() - t0)
        plans[gi] = paths_from_joint(r.path)
    merges = 0
    while True:
        conflict = None
        for a, b in itertools.combinations(range(len(groups)), 2):
            if plans_conflict(plans[a], plans[b]) is not None:
                conflict = (a, b)
                break
        if conflict is None:
            break
        a, b = conflict
        merged = groups[a] + groups[b]
        r = solve(inst.sub_instance(merged))
        expansions += r.expansions
        generated += r.generated
        merges += 1
        if not r.solved:
            return Result(None, INF, expansions, generated, time.perf_counter() - t0,
                          {"groups": groups, "aborted": r.info.get("aborted", False)})
        new_groups = [grp for gi, grp in enumerate(groups) if gi not in (a, b)]
        new_plans = {ni: plans[gi] for ni, gi in
                     enumerate(gi for gi in range(len(groups)) if gi not in (a, b))}
        new_groups.append(merged)
        new_plans[len(new_groups) - 1] = paths_from_joint(r.path)
        groups, plans = new_groups, new_plans
    paths = [None] * inst.k
    for gi, grp in enumerate(groups):
        for local, i in enumerate(grp):
            paths[i] = plans[gi][local]
    joint = joint_from_paths(paths)
    cost = active_cost(paths, inst.goals)
    return Result(joint, cost, expansions, generated, time.perf_counter() - t0,
                  {"groups": groups, "merges": merges,
                   "largest_group": max(len(g) for g in groups)})


# ---------------------------------------------------------------------------
# M* with collision sets and backpropagation (Wagner and Choset 2011, 2015)
# ---------------------------------------------------------------------------
@dataclass
class MstarNode:
    config: tuple
    g: float = INF
    parent: tuple = None
    collision_set: set = field(default_factory=set)
    back_set: set = field(default_factory=set)
    in_open: bool = False


def limited_neighbours(node, inst, pol):
    """Agents in the collision set may move anywhere; the rest follow their policy."""
    options = []
    for i, v in enumerate(node.config):
        if i in node.collision_set:
            options.append(agent_moves(inst.graph, v))
        else:
            options.append([pol.step(i, v)])
    return itertools.product(*options)


def mstar(inst, trace=False, max_expansions=None, max_generated=None):
    """Basic M*: joint A* that expands only along the individual policies
    unless a collision has been found downstream.  Returns a Result whose
    info holds the final collision sets and, if ``trace`` is set, a list of
    expansion records (step, config, g, h, collision set, successors)."""
    t0 = time.perf_counter()
    pol = Policies(inst)
    start, goal = tuple(inst.starts), tuple(inst.goals)
    goals = inst.goals
    if pol.h(start) == INF:
        return Result(None, INF, 0, 0, time.perf_counter() - t0)
    nodes = {start: MstarNode(start, 0)}
    counter = itertools.count()
    open_heap = []

    def push(node):
        node.in_open = True
        heapq.heappush(open_heap, (node.g + pol.h(node.config), -node.g,
                                   next(counter), node.config))

    def backprop(config, colset):
        """Add colset to the collision set of config and of all its ancestors."""
        stack = [(config, colset)]
        while stack:
            cfg, cs = stack.pop()
            node = nodes[cfg]
            if cs <= node.collision_set:
                continue
            node.collision_set |= cs
            if not node.in_open and node.g < INF:
                push(node)                    # re-expand with more neighbours
            for p in node.back_set:
                stack.append((p, node.collision_set))

    push(nodes[start])
    expansions = generated = 0
    records = []
    while open_heap:
        f, neg_g, _, cfg = heapq.heappop(open_heap)
        node = nodes[cfg]
        if -neg_g > node.g:
            continue                          # stale entry (cheaper path found)
        if not node.in_open:
            continue                          # already expanded since this push
        node.in_open = False
        if cfg == goal:
            path = []
            while cfg is not None:
                path.append(cfg)
                cfg = nodes[cfg].parent
            info = {"collision_sets": {c: frozenset(n.collision_set) for c, n in nodes.items()},
                    "max_collision_set": max(len(n.collision_set) for n in nodes.values()),
                    "trace": records}
            return Result(path[::-1], node.g, expansions, generated,
                          time.perf_counter() - t0, info)
        expansions += 1
        if ((max_expansions is not None and expansions > max_expansions) or
                (max_generated is not None and generated > max_generated)):
            return Result(None, INF, expansions, generated, time.perf_counter() - t0,
                          {"aborted": True})
        rec = {"step": expansions, "config": cfg, "g": node.g, "h": pol.h(cfg),
               "collision_set": frozenset(node.collision_set), "successors": [],
               "collisions": []}
        for nxt in limited_neighbours(node, inst, pol):
            generated += 1
            child = nodes.get(nxt)
            if child is None:
                child = nodes[nxt] = MstarNode(nxt)
            child.back_set.add(cfg)
            col = collisions(cfg, nxt)
            if col:
                # a vertex collision belongs to the configuration nxt, a swap
                # collision only to the edge cfg -> nxt
                child.collision_set |= vertex_collisions(nxt)
                rec["collisions"].append((nxt, frozenset(col)))
                backprop(cfg, col | child.collision_set)
                continue
            backprop(cfg, child.collision_set)
            new_g = node.g + step_cost(cfg, nxt, goals)
            if new_g < child.g:
                child.g = new_g
                child.parent = cfg
                push(child)
                rec["successors"].append((nxt, new_g))
        if trace:
            records.append(rec)
    return Result(None, INF, expansions, generated, time.perf_counter() - t0,
                  {"collision_sets": {c: frozenset(n.collision_set) for c, n in nodes.items()},
                   "trace": records})


# ---------------------------------------------------------------------------
# Push-and-swap primitives on an abstract graph (Luna and Bekris 2011)
# ---------------------------------------------------------------------------
class PushSwapState:
    """Positions of the agents on a graph and the sequential move log."""

    def __init__(self, inst):
        self.inst = inst
        self.graph = inst.graph
        self.pos = {i: s for i, s in enumerate(inst.starts)}
        self.moves = []                        # (agent, from, to), one at a time
        self.locked = set()                    # agents parked at their goal

    def at(self, v):
        for i, p in self.pos.items():
            if p == v:
                return i
        return None

    def empty(self, v):
        return self.at(v) is None

    def move(self, agent, to):
        frm = self.pos[agent]
        assert to in self.graph.neighbours(frm) and self.empty(to), (agent, frm, to)
        self.pos[agent] = to
        self.moves.append((agent, frm, to))

    def undo_by_position(self, moves):
        """Undo recorded moves in reverse order, moving whoever stands there."""
        for _, frm, to in reversed(moves):
            self.move(self.at(to), frm)

    # -- clear: shift the chain of agents from v to the nearest empty vertex --
    def clear(self, v, avoid):
        """Make v empty by shifting agents towards the nearest empty vertex
        that is reachable without touching ``avoid``; False if impossible."""
        if self.empty(v):
            return True
        forbidden = set(avoid) | {self.pos[i] for i in self.locked}
        parent = {v: None}
        queue = deque([v])
        target = None
        while queue and target is None:
            u = queue.popleft()
            for w in self.graph.neighbours(u):
                if w in parent or w in forbidden:
                    continue
                parent[w] = u
                if self.empty(w):
                    target = w
                    break
                queue.append(w)
        if target is None:
            return False
        chain = [target]
        while parent[chain[-1]] is not None:
            chain.append(parent[chain[-1]])
        chain.reverse()                        # v, ..., target
        for a, b in reversed(list(zip(chain, chain[1:]))):
            self.move(self.at(a), b)           # shift from the empty end back
        return True

    # -- push: move an agent along a path, clearing the way ------------------
    def push(self, agent, path):
        """Move ``agent`` along ``path`` (path[0] is its position).  Stops and
        returns False when a locked agent blocks the way (a swap is needed)."""
        for nxt in path[1:]:
            blocker = self.at(nxt)
            if blocker is not None:
                if blocker in self.locked:
                    return False
                # the blocker (and the chain behind it) leaves the path
                if not self.clear(nxt, avoid=set(path) - {nxt}):
                    return False
            self.move(agent, nxt)
        return True

    # -- swap: exchange two adjacent agents at a vertex of degree >= 3 -------
    def swap(self, a, b):
        """Exchange the positions of the adjacent agents a and b without
        changing where any other agent stands.  Returns False on failure."""
        pa = self.pos[a]
        assert self.pos[b] in self.graph.neighbours(pa)
        dist = bfs_distances(self.graph, pa)
        junctions = sorted((d, v) for v, d in dist.items() if self.graph.degree(v) >= 3)
        for _, v in junctions:
            saved_pos, saved_moves = dict(self.pos), list(self.moves)
            mark = len(self.moves)
            if self._swap_at(a, b, v):
                return True
            self.pos, self.moves = saved_pos, saved_moves      # roll back
            del self.moves[mark:]
        return False

    def _swap_at(self, a, b, v):
        # multipush: the agent nearer to v leads along a shortest path to v,
        # the other one follows one step behind
        path_a = bfs_path(self.graph, self.pos[a], v, avoid={self.pos[b]})
        path_b = bfs_path(self.graph, self.pos[b], v, avoid={self.pos[a]})
        if path_a is None and path_b is None:
            return False
        if path_b is not None and (path_a is None or len(path_b) < len(path_a)):
            a, b, path = b, a, path_b
        else:
            path = path_a
        mark = len(self.moves)
        for nxt in path[1:]:
            if not self.empty(nxt):
                if not self.clear(nxt, avoid={self.pos[a], self.pos[b], nxt}):
                    return False
            prev_a = self.pos[a]
            self.move(a, nxt)
            self.move(b, prev_a)
        u = self.pos[b]                        # b is right behind a at v
        # clear two other neighbours of v
        others = [n for n in self.graph.neighbours(v) if n != u]
        free = []
        for n in others:
            if self.empty(n) or self.clear(n, avoid={v, u} | set(free)):
                free.append(n)
            if len(free) == 2:
                break
        if len(free) < 2:
            return False
        n1, n2 = free
        prep = self.moves[mark:]               # everything before the exchange
        # the exchange itself: six moves
        self.move(a, n1)
        self.move(b, v)
        self.move(b, n2)
        self.move(a, v)
        self.move(a, u)
        self.move(b, v)
        # undo the preparation with the two agents exchanged
        self.undo_by_position(prep)
        return True


def push_and_swap(inst):
    """A small push-and-swap driver for the examples of the chapter.

    Agents are solved in index order; an agent pushes along its shortest
    path and swaps with a locked agent that blocks it.  A locked agent that
    was displaced by a swap is released and solved again afterwards.  This
    driver has no 'resolve' step and no graph decomposition, so it is not
    the complete algorithm of the papers; it returns None when stuck.
    """
    st = PushSwapState(inst)
    pending = list(range(inst.k))
    guard = 0
    while pending:
        guard += 1
        if guard > 50 * inst.k:
            return None
        a = pending.pop(0)
        goal = inst.goals[a]
        while st.pos[a] != goal:
            path = bfs_path(st.graph, st.pos[a], goal)
            if path is None:
                return None
            if st.push(a, path):
                break
            # a locked agent blocks the next step: swap with it
            blocker = st.at(path[path.index(st.pos[a]) + 1])
            if blocker is None or not st.swap(a, blocker):
                return None
            st.locked.discard(blocker)
            if blocker not in pending:
                pending.append(blocker)
        st.locked.add(a)
    return st


def sequential_to_paths(st):
    """Turn the sequential move log into per-agent paths, one move per step."""
    k = st.inst.k
    paths = [[s] for s in st.inst.starts]
    for agent, frm, to in st.moves:
        for i in range(k):
            paths[i].append(to if i == agent else paths[i][-1])
    return paths


# ---------------------------------------------------------------------------
# The instances of the chapter
# ---------------------------------------------------------------------------
def worked_example():
    """Two drones meet head-on in an aisle with one bay; a third drone flies
    along a second aisle that is joined to the first only at the east wall."""
    rows = [
        ".....",       # y = 3: upper aisle (agent 3)
        "@@@@.",       # y = 2: passage at (4, 2)
        ".....",       # y = 1: lower aisle (agents 1 and 2)
        "@.@@@",       # y = 0: bay at (1, 0)
    ]
    graph = Graph.from_map(rows)
    starts = [(0, 1), (4, 1), (0, 3)]
    goals = [(4, 1), (0, 1), (4, 3)]
    return MAPFInstance(graph, starts, goals, "worked example"), rows


def swap_example():
    """A corridor c0..c4 with a spur s at c3; the agents a and b must swap."""
    graph = Graph.from_edges([("c0", "c1"), ("c1", "c2"), ("c2", "c3"),
                              ("c3", "c4"), ("c3", "s")])
    return MAPFInstance(graph, ["c0", "c1"], ["c1", "c0"], "swap example")


def push_example():
    """Agent a walks along a path; b (on the path) and c (behind b in a side
    branch) are shifted one step into the branch to let a pass."""
    graph = Graph.from_edges([("v0", "v1"), ("v1", "v2"), ("v2", "v3"),
                              ("v3", "v4"), ("v2", "w1"), ("w1", "w2")])
    return MAPFInstance(graph, ["v0", "v2", "w1"], ["v4", "v2", "w1"], "push example")


def random_instance(rng, width, height, k, density=0.15):
    """A random connected map with k agents on distinct free cells."""
    while True:
        rows = ["".join("@" if rng.random() < density else "." for _ in range(width))
                for _ in range(height)]
        graph = Graph.from_map(rows)
        cells = graph.vertices
        if len(cells) < 2 * k + 2:
            continue
        comp = bfs_distances(graph, cells[0])
        if len(comp) != len(cells):
            continue
        starts = rng.sample(cells, k)
        goals = rng.sample(cells, k)
        return MAPFInstance(graph, starts, goals, "random"), rows


def joint_state_counts(n_vertices, k, branching=5):
    """|V|^k joint configurations, collision-free ones, and (b+1)^k joint moves."""
    total = n_vertices ** k
    free = 1
    for i in range(k):
        free *= n_vertices - i
    return total, free, branching ** k


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _self_test():
    rng = random.Random(11)

    # 1. Collision detection: vertex, swap, following.
    assert collisions(((0, 0), (1, 0)), ((1, 0), (1, 0))) == {0, 1}
    assert collisions(((0, 0), (1, 0)), ((1, 0), (0, 0))) == {0, 1}
    assert collisions(((0, 0), (1, 0)), ((1, 0), (2, 0))) == set()
    assert collisions(((0, 0), (1, 0), (5, 5)), ((0, 0), (0, 0), (5, 5))) == {0, 1}

    # 2. Worked example: the trace of the chapter (every quoted number).
    inst, rows = worked_example()
    pol = Policies(inst)
    start = tuple(inst.starts)
    assert pol.h(start) == 12
    assert pol.step(0, (0, 1)) == (1, 1) and pol.step(1, (4, 1)) == (3, 1)
    assert pol.step(2, (0, 3)) == (1, 3) and pol.step(0, (4, 1)) == (4, 1)
    m = mstar(inst, trace=True)
    assert m.solved and m.cost == 15
    assert m.expansions == 31 and m.generated == 127
    paths = paths_from_joint(m.path)
    assert validate(paths, inst)
    assert active_cost(paths, inst.goals) == 15
    assert sum_of_costs(paths, inst.goals) == 15 and makespan(paths) == 7
    assert paths[0] == [(0, 1), (1, 1), (1, 1), (1, 0), (1, 1), (2, 1), (3, 1), (4, 1)]
    assert paths[1] == [(4, 1), (3, 1), (2, 1), (1, 1), (0, 1), (0, 1), (0, 1), (0, 1)]
    assert paths[2] == [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (4, 3), (4, 3), (4, 3)]
    assert m.info["max_collision_set"] == 2
    csets = m.info["collision_sets"]
    assert all(2 not in cs for cs in csets.values())      # agent 3 never coupled
    assert csets[start] == frozenset({0, 1})
    assert all(cs == frozenset({0, 1}) for cs in csets.values() if cs)
    assert (sum(1 for cs in csets.values() if cs), len(csets)) == (19, 55)
    trace = m.info["trace"]
    v1 = ((1, 1), (3, 1), (1, 3))
    assert trace[0]["config"] == start and trace[0]["collision_set"] == frozenset()
    assert [s for s, _ in trace[0]["successors"]] == [v1]
    assert trace[1]["config"] == v1 and trace[1]["collision_set"] == frozenset()
    assert trace[1]["collisions"] == [(((2, 1), (2, 1), (2, 3)), frozenset({0, 1}))]
    assert trace[1]["successors"] == []
    assert trace[2]["config"] == v1 and trace[2]["collision_set"] == frozenset({0, 1})
    assert len(trace[2]["successors"]) == 11
    assert trace[3]["config"] == start and trace[3]["collision_set"] == frozenset({0, 1})
    assert len(trace[3]["successors"]) == 5
    f_values = [r["g"] + r["h"] for r in trace]
    assert f_values == sorted(f_values) and f_values[0] == 12 and f_values[-1] == 15
    assert sum(1 for r in trace if r["collision_set"]) == 12   # expansions with C = {1,2}
    assert sum(1 for r in trace if r["g"] + r["h"] == 12) == 4
    assert trace[28]["config"] == ((1, 1), (0, 1), (4, 3)) and trace[28]["collision_set"] == frozenset()
    j = joint_astar(inst)
    assert j.solved and j.cost == 15 and validate(paths_from_joint(j.path), inst)
    assert (j.expansions, j.generated) == (24, 612)
    od = joint_astar(inst, operator_decomposition=True)
    assert od.solved and od.cost == 15 and validate(paths_from_joint(od.path), inst)
    assert (od.expansions, od.generated) == (100, 292)
    idr = independence_detection(inst)
    assert idr.solved and idr.cost == 15 and validate(paths_from_joint(idr.path), inst)
    assert sorted(map(sorted, idr.info["groups"])) == [[0, 1], [2]]
    assert (idr.expansions, idr.generated, idr.info["merges"]) == (27, 162, 1)
    print("worked example: M* %d expansions, %d generated, cost %d; joint A* %d/%d;"
          " OD %d/%d; ID %d/%d, groups %s" % (
              m.expansions, m.generated, m.cost, j.expansions, j.generated,
              od.expansions, od.generated, idr.expansions, idr.generated,
              idr.info["groups"]))

    # 3. M* matches joint A* on random tiny instances (cost and validity).
    checked = 0
    for _ in range(40):
        k = rng.choice([2, 2, 3, 3, 4])
        inst_r, _ = random_instance(rng, 5, 4, k, 0.2)
        j = joint_astar(inst_r, max_generated=400000)
        if j.info.get("aborted"):
            continue
        m = mstar(inst_r)
        idr = independence_detection(inst_r)
        od = joint_astar(inst_r, operator_decomposition=True)
        assert m.solved == j.solved == idr.solved == od.solved
        if j.solved:
            assert m.cost == j.cost == idr.cost == od.cost, (m.cost, j.cost, idr.cost, od.cost)
            for r in (m, j, idr, od):
                p = paths_from_joint(r.path)
                assert validate(p, inst_r) and active_cost(p, inst_r.goals) == j.cost
            assert m.expansions <= j.expansions + 1
        checked += 1
    assert checked >= 25
    print("random instances checked against joint A*: %d" % checked)

    # 4. Unsolvable instance: two agents must swap in a plain corridor.
    corridor = MAPFInstance(Graph.from_map(["...."]), [(0, 0), (3, 0)], [(3, 0), (0, 0)])
    assert not mstar(corridor).solved and not joint_astar(corridor).solved
    assert not independence_detection(corridor).solved

    # 5. Costs: waiting at the goal is free, leaving it again is not.
    goals = [(2, 0)]
    p = [[(0, 0), (1, 0), (2, 0), (2, 0), (2, 0)]]
    assert active_cost(p, goals) == 2 and sum_of_costs(p, goals) == 2
    p = [[(0, 0), (1, 0), (2, 0), (2, 0), (1, 0), (2, 0)]]
    assert active_cost(p, goals) == 4 and sum_of_costs(p, goals) == 5

    # 6. Push-and-swap primitives.
    inst_s = swap_example()
    st = push_and_swap(inst_s)
    assert st is not None and all(st.pos[i] == g for i, g in enumerate(inst_s.goals))
    seq = sequential_to_paths(st)
    assert validate(seq, inst_s)
    n_moves = len(st.moves)
    j = joint_astar(inst_s)
    jp = paths_from_joint(j.path)
    print("swap example: push-and-swap %d sequential moves (makespan %d, sum of costs %d);"
          " optimal joint plan: makespan %d, sum of costs %d" % (
              n_moves, makespan(seq), sum_of_costs(seq, inst_s.goals),
              makespan(jp), sum_of_costs(jp, inst_s.goals)))
    assert n_moves == 14 and makespan(seq) == 14 and sum_of_costs(seq, inst_s.goals) == 27
    assert makespan(jp) == 7 and sum_of_costs(jp, inst_s.goals) == 14
    # the pure swap macro: 4 d + 6 moves when the leader is d steps from the junction
    for d in (1, 2, 3, 4):
        edges = ([("c%d" % i, "c%d" % (i + 1)) for i in range(d + 2)]
                 + [("c%d" % (d + 1), "s")])
        g = Graph.from_edges(edges)
        st2 = PushSwapState(MAPFInstance(g, ["c1", "c0"], ["c0", "c1"]))
        assert st2.swap(0, 1) and st2.pos == {0: "c0", 1: "c1"}
        assert len(st2.moves) == 4 * d + 6, (d, len(st2.moves))
        assert validate(sequential_to_paths(st2), MAPFInstance(g, ["c1", "c0"], ["c0", "c1"]))
    inst_p = push_example()
    st3 = PushSwapState(inst_p)
    assert st3.push(0, bfs_path(inst_p.graph, "v0", "v4"))
    assert st3.pos == {0: "v4", 1: "w1", 2: "w2"} and len(st3.moves) == 6
    assert st3.moves[1:3] == [(2, "w1", "w2"), (1, "v2", "w1")]     # the chain shift
    st4 = push_and_swap(inst_p)
    assert st4 is not None and all(st4.pos[i] == g for i, g in enumerate(inst_p.goals))
    assert len(st4.moves) == 8 and validate(sequential_to_paths(st4), inst_p)
    jp = paths_from_joint(joint_astar(inst_p).path)
    print("push example: push-and-swap %d moves; optimal joint plan: makespan %d,"
          " sum of costs %d" % (len(st4.moves), makespan(jp), sum_of_costs(jp, inst_p.goals)))
    assert makespan(jp) == 4 and sum_of_costs(jp, inst_p.goals) == 10

    # 7. State-space counts used in the table of the chapter.
    assert joint_state_counts(64, 2) == (4096, 4032, 25)
    assert joint_state_counts(64, 5)[0] == 64 ** 5
    print("ch11_mstar: all self-tests passed")


if __name__ == "__main__":
    _self_test()
