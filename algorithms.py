# algorithms.py - BFS, A*, IDA* and Hill Climbing for the 8-puzzle
# Every function returns a dictionary with:
#   path (list of states from start to the end), expanded_nodes, time,
#   solved (True/False), explored (first 200 expanded states), message
import time
import heapq
from collections import deque
from puzzle import GOAL, get_neighbors, manhattan

MAX_EXPLORED = 200  # only keep this many states for the animation


def make_result(path, expanded, start_time, solved, explored, message):
    return {
        "path": path,
        "expanded_nodes": expanded,
        "time": time.perf_counter() - start_time,  # algorithm time only
        "solved": solved,
        "explored": explored,
        "message": message,
    }


def build_path(parents, state):
    """Follow parent links back to the start, then reverse."""
    path = [state]
    while parents[state] is not None:
        state = parents[state]
        path.append(state)
    path.reverse()
    return path


def bfs(start):
    """Breadth-First Search: expands the shallowest node first (uses a queue)."""
    t0 = time.perf_counter()
    queue = deque([start])
    parents = {start: None}  # also works as the 'visited' set
    expanded = 0
    explored = []
    while queue:
        state = queue.popleft()
        expanded += 1
        if len(explored) < MAX_EXPLORED:
            explored.append(state)
        if state == GOAL:
            return make_result(build_path(parents, state), expanded, t0, True, explored, "Solved")
        for _, nxt in get_neighbors(state):
            if nxt not in parents:
                parents[nxt] = state
                queue.append(nxt)
    return make_result([start], expanded, t0, False, explored, "No solution")


def astar(start):
    """A*: expands the node with the smallest f = g + h (g = cost so far, h = Manhattan)."""
    t0 = time.perf_counter()
    counter = 0  # tie-breaker so the heap never compares states
    heap = [(manhattan(start), counter, 0, start)]  # (f, counter, g, state)
    parents = {start: None}
    best_g = {start: 0}
    expanded = 0
    explored = []
    while heap:
        f, _, g, state = heapq.heappop(heap)
        if g > best_g[state]:
            continue  # old, worse entry for this state: skip it
        expanded += 1
        if len(explored) < MAX_EXPLORED:
            explored.append(state)
        if state == GOAL:
            return make_result(build_path(parents, state), expanded, t0, True, explored, "Solved")
        for _, nxt in get_neighbors(state):
            new_g = g + 1  # every move costs 1
            if nxt not in best_g or new_g < best_g[nxt]:
                best_g[nxt] = new_g
                parents[nxt] = state
                counter += 1
                heapq.heappush(heap, (new_g + manhattan(nxt), counter, new_g, nxt))
    return make_result([start], expanded, t0, False, explored, "No solution")


def idastar(start):
    """IDA*: repeated depth-first search with a growing f-limit. Uses little memory."""
    t0 = time.perf_counter()
    expanded = 0
    explored = []

    def search(path, g, limit):
        """Returns (found, new_limit). 'path' is the current branch only."""
        nonlocal expanded
        state = path[-1]
        f = g + manhattan(state)
        if f > limit:
            return False, f  # too expensive: report the f that broke the limit
        if state == GOAL:
            return True, f
        expanded += 1
        if len(explored) < MAX_EXPLORED:
            explored.append(state)
        smallest = float("inf")
        for _, nxt in get_neighbors(state):
            if nxt in path:
                continue  # do not walk in circles
            path.append(nxt)
            found, value = search(path, g + 1, limit)
            if found:
                return True, value
            path.pop()
            smallest = min(smallest, value)
        return False, smallest

    limit = manhattan(start)
    path = [start]
    while True:
        found, value = search(path, 0, limit)
        if found:
            return make_result(path, expanded, t0, True, explored, "Solved")
        if value == float("inf"):
            return make_result([start], expanded, t0, False, explored, "No solution")
        limit = value  # next round: allow the smallest f that was cut off


def hill_climbing(start):
    """Steepest-ascent Hill Climbing on Manhattan distance.
    Always moves to the best neighbor. Stops when no neighbor is strictly better,
    so it can get stuck at a local optimum (this is real, not hidden)."""
    t0 = time.perf_counter()
    state = start
    path = [state]
    explored = []
    expanded = 0
    while True:
        expanded += 1
        if len(explored) < MAX_EXPLORED:
            explored.append(state)
        if state == GOAL:
            return make_result(path, expanded, t0, True, explored, "Solved")
        best = min((n for _, n in get_neighbors(state)), key=manhattan)
        if manhattan(best) >= manhattan(state):  # not strictly better
            return make_result(path, expanded, t0, False, explored, "Stuck at local optimum")
        state = best
        path.append(state)


ALGORITHMS = {
    "BFS": bfs,
    "A* (Manhattan)": astar,
    "IDA* (Manhattan)": idastar,
    "Hill Climbing": hill_climbing,
}
