# 8-Puzzle AI Solver - AIM 315 (Intelligent Agent & Search Problem)

## 1. Problem description
The 8-puzzle is a 3x3 board with tiles 1 to 8 and one empty space (the blank). The agent slides tiles into the blank until the board looks like the goal:

```
1 2 3
4 5 6
7 8 _
```

The program solves the puzzle with four search algorithms and compares them.

## 2. Agent type and environment
The agent is a **goal-based agent** with a **problem-solving (search) approach**. It does not react blindly. It first searches for a sequence of moves in its model of the puzzle, then executes that sequence.

How it interacts with the environment:
- **Percept:** the current board (the state).
- **Action:** move the blank Up, Down, Left or Right.
- **Process:** the agent searches in its head (the program), finds a path, then performs the moves one by one on the board.

The environment is fully observable, deterministic, static, discrete and single-agent. Because of this, planning ahead with search works well.

## 3. PEAS
| Part | Description |
|---|---|
| Performance measure | Solve the puzzle; fewer moves (path cost); fewer expanded nodes; less time |
| Environment | The 3x3 board with 8 tiles and a blank |
| Actuators | Moving the blank Up / Down / Left / Right |
| Sensors | Reading the current positions of all tiles |

## 4. Problem formulation
- **Initial state:** any solvable arrangement, e.g. `(1,2,3,4,0,6,7,5,8)` (0 = blank).
- **State space:** all arrangements of the 9 numbers: 9! = 362,880. Only half (181,440) can reach the goal.
- **Actions:** move the blank Up, Down, Left, Right (only if it stays on the board).
- **Goal test:** state equals `(1,2,3,4,5,6,7,8,0)`.
- **Path cost:** every move costs 1, so the cost equals the number of moves.

Solvability: count inversions (pairs of tiles in the wrong order, ignoring the blank). If the count is odd, the puzzle is unsolvable and the program rejects it.

Heuristic: **Manhattan distance** = for every tile, rows away + columns away from its goal square, summed. It never overestimates, so it is admissible.

## 5. Algorithms
**BFS (uninformed).** Uses a queue and expands the shallowest node first. It is complete and finds the shortest path, but it needs a lot of memory and expands many nodes.

**A\* with Manhattan (informed).** Expands the node with the smallest f = g + h (g = moves so far, h = Manhattan distance). Because h is admissible, A* is complete and optimal, and it expands far fewer nodes than BFS. It still stores all generated nodes.

**IDA\* with Manhattan (memory-bounded).** Runs depth-first search with a limit on f. If no solution is found, the limit grows to the smallest f that was cut off, and it repeats. It is optimal like A* but only stores the current path, so it uses very little memory. It may repeat work.

**Hill Climbing (local search, steepest ascent).** Looks at all neighbors, moves to the one with the lowest Manhattan distance, and stops when no neighbor is strictly better. It is fast and uses almost no memory, but it is not complete: it can get stuck at a local optimum. The program reports this as "Stuck at local optimum".

## 6. Results (real runs)
Time is the best of 3 runs of the algorithm only (no animation). Path = number of moves.

| Puzzle | Algorithm | Solved | Path | Expanded nodes | Time (s) |
|---|---|---|---|---|---|
| Easy `1,2,3,4,0,6,7,5,8` | BFS | Yes | 2 | 9 | 0.00002 |
| | A* | Yes | 2 | 3 | 0.00001 |
| | IDA* | Yes | 2 | 2 | 0.00001 |
| | Hill Climbing | Yes | 2 | 3 | 0.00002 |
| Medium `8,1,3,4,0,2,7,6,5` | BFS | Yes | 14 | 5,961 | 0.01977 |
| | A* | Yes | 14 | 77 | 0.00067 |
| | IDA* | Yes | 14 | 104 | 0.00094 |
| | Hill Climbing | **No (stuck)** | 2 (moves made) | 3 | 0.00005 |
| Hard `8,6,7,2,5,4,3,0,1` | BFS | Yes | 31 | 181,439 | 0.40901 |
| | A* | Yes | 31 | 20,291 | 0.11615 |
| | IDA* | Yes | 31 | 14,195 | 0.06867 |
| | Hill Climbing | **No (stuck)** | 1 (moves made) | 2 | 0.00001 |

(Times depend on the computer; the other numbers are always the same.)

## 7. Comparison
- BFS, A* and IDA* always give the **same optimal cost** (2, 14, 31).
- BFS expands the most nodes. On the hard puzzle it expanded about 9 times more than A*.
- A* expands the fewest nodes in the medium case; IDA* expands fewer on the hard case (it counts expansions across repeated rounds but does not keep a closed list). Both are far better than BFS.
- IDA* is the best for memory, since it keeps only one path.
- Hill Climbing is the fastest per run but failed on the medium and hard puzzles.

## 8. Discussion
Information (the heuristic) makes search much smarter: A* and IDA* use Manhattan distance to ignore bad directions. BFS has no idea where the goal is, so it explores everything level by level.

Hill Climbing only looks one step ahead. On the medium and hard puzzles every neighbor was no better than the current state, so it stopped. The 8-puzzle has such local optima (plateaus and dead ends). It works only on easy puzzles where the heuristic goes down every step. Fixes exist (random restarts, simulated annealing) but they are outside this project.

The trade-off: BFS and A* use much memory (they store many nodes); IDA* uses little memory but repeats work; Hill Climbing uses almost nothing but gives no guarantee.

## 9. Conclusion
For the 8-puzzle, A* and IDA* with Manhattan distance are the best choices: they are optimal and fast. A* is simplest, IDA* saves memory. BFS is optimal but slow and memory-heavy. Hill Climbing is quick but incomplete, and the app shows this honestly when it gets stuck.

## 10. Screenshots
- [ ] Screenshot 1: main window with a custom state
- [ ] Screenshot 2: "Searching..." animation
- [ ] Screenshot 3: solved board (green) with cost and move list
- [ ] Screenshot 4: Hill Climbing stuck (red board)
- [ ] Screenshot 5: Performance Comparison charts with all 4 algorithms
- [ ] Screenshot 6: error message for an unsolvable state
