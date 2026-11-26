# puzzle.py - the 8-puzzle problem: state, moves, solvability, heuristic
import random

# A state is a tuple of 9 numbers (read row by row). 0 is the blank.
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Moving the blank: name -> (row change, column change)
MOVES = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}


def parse_state(text):
    """Turn text like '1,2,3,4,0,6,7,5,8' into a tuple.
    Raises ValueError with a clear message if the text is not valid."""
    parts = text.replace(" ", "").split(",")
    try:
        numbers = tuple(int(p) for p in parts)
    except ValueError:
        raise ValueError("Use only numbers separated by commas.")
    if len(numbers) != 9:
        raise ValueError("Enter exactly 9 numbers.")
    if sorted(numbers) != list(range(9)):
        raise ValueError("Use each number from 0 to 8 exactly once.")
    return numbers


def is_solvable(state):
    """Count inversions (pairs of tiles in the wrong order, ignoring 0).
    For a 3x3 board the puzzle is solvable only if the count is even."""
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions % 2 == 0


def is_goal(state):
    return state == GOAL


def get_neighbors(state):
    """Return a list of (move_name, new_state) for every legal blank move."""
    blank = state.index(0)
    row, col = divmod(blank, 3)
    result = []
    for name, (dr, dc) in MOVES.items():
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:  # stay inside the board
            target = new_row * 3 + new_col
            new_state = list(state)
            new_state[blank], new_state[target] = new_state[target], new_state[blank]
            result.append((name, tuple(new_state)))
    return result


def manhattan(state):
    """Sum of (row distance + column distance) of every tile from its goal spot."""
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue  # the blank is not counted
        goal_index = tile - 1  # tile 1 belongs at index 0, tile 2 at 1, ...
        total += abs(index // 3 - goal_index // 3) + abs(index % 3 - goal_index % 3)
    return total


def shuffle_state(moves=60):
    """Start from the goal and make random legal moves, so it is always solvable."""
    state = GOAL
    for _ in range(moves):
        state = random.choice(get_neighbors(state))[1]
    return state


def moves_from_path(path):
    """Turn a list of states into a list of blank moves like ['Up', 'Left']."""
    names = {-3: "Up", 3: "Down", -1: "Left", 1: "Right"}
    moves = []
    for a, b in zip(path, path[1:]):
        moves.append(names[b.index(0) - a.index(0)])
    return moves
