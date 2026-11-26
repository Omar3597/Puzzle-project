# test_puzzle.py - run with: python test_puzzle.py
from puzzle import GOAL, parse_state, is_solvable, shuffle_state, get_neighbors
from algorithms import bfs, astar, idastar, hill_climbing

EASY = (1, 2, 3, 4, 0, 6, 7, 5, 8)
MEDIUM = (1, 2, 3, 0, 4, 6, 7, 5, 8)
HARD = (8, 1, 3, 4, 0, 2, 7, 6, 5)


def check_path(path, start):
    """Every step must be a legal move, starting at start."""
    assert path[0] == start
    for a, b in zip(path, path[1:]):
        assert b in [n for _, n in get_neighbors(a)]


def test_same_cost():
    for start in (GOAL, EASY, MEDIUM, HARD, shuffle_state(40)):
        results = [f(start) for f in (bfs, astar, idastar)]
        costs = [len(r["path"]) - 1 for r in results]
        assert all(r["solved"] and r["path"][-1] == GOAL for r in results)
        for r in results:
            check_path(r["path"], start)
        assert costs[0] == costs[1] == costs[2], costs
        print("same cost OK:", costs)


def test_unsolvable():
    for text in ("1,2,3,4,5,6,8,7,0", "1,2,3", "1,1,3,4,5,6,7,8,0", "a,b,c"):
        try:
            state = parse_state(text)
            assert not is_solvable(state), text
        except ValueError:
            pass
    assert not is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0))
    assert is_solvable(HARD)
    print("unsolvable rejected OK")


def test_hill_climbing():
    ok = hill_climbing(EASY)
    assert ok["solved"]
    stuck = None
    for _ in range(200):  # find a puzzle where it really gets stuck
        s = shuffle_state(60)
        r = hill_climbing(s)
        if not r["solved"]:
            stuck = r
            break
    assert stuck is not None and stuck["message"] == "Stuck at local optimum"
    assert stuck["path"][-1] != GOAL
    print("hill climbing failure handled OK, stuck path length", len(stuck["path"]) - 1)


test_same_cost()
test_unsolvable()
test_hill_climbing()
print("ALL TESTS PASSED")
