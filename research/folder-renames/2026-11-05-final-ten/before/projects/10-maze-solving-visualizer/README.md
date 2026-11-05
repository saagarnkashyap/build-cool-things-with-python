# Maze-Solving Visualizer

Compare independent breadth-first and depth-first searches on the same maze, with synchronized exploration animation, highlighted routes, and measured counts.

## Learning objectives

- Use a deque for BFS and a stack for DFS.
- Reconstruct paths from parent links and count explored nodes.
- Distinguish route discovery from a shortest-path guarantee.

## Installation

Only Python 3.12+ standard-library modules are required. The optional desktop interface uses Tk, included with many Python installations.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/16-maze-solving-visualizer`. Activate your Python environment first.

## Usage

```powershell
python main.py
python main.py --predefined
python main.py --predefined --solve
python main.py --seed 17 --rows 21 --cols 31 --solve
```

Generate creates a reproducible perfect maze from the seed. Predefined loads a cyclic maze with two routes. Animate starts both searches, Pause/resume controls playback, and Step advances exploration. Teal and violet cells were explored; gold cells are the final route. Green is the start and red is the exit. Path length counts edges, not cells; explored counts include each processed cell once. Generated dimensions must be odd and between 5 and 61.

BFS uses a FIFO queue. With equal-cost edges, all cells at distance k are processed before any cell at distance k+1, so the first discovery of the goal has minimum edge count. DFS uses a LIFO stack and follows a branch before alternatives; it can reach the goal along a longer route. The predefined example demonstrates BFS = 8 edges and DFS = 12. Both algorithms report an empty path if the goal is unreachable. Neighbor order is down, right, up, left; tie-breaking affects exploration. A generated perfect maze has only one route, so its two final path lengths agree even when explored counts differ.

## Tests and representative output

```powershell
python -m unittest discover -s tests -v
```

[Application capture](screenshots/app.png). See [samples](samples/) for outputs from real execution and
[exercises](exercises.md) for follow-up challenges. The repository-wide test
command is `python scripts/run_project_tests.py` from the repository root.

## Troubleshooting

For a Tk display error, use `--solve` in a headless terminal. Use odd dimensions. The seed entry must be a whole number. Pause does not change the computed result; it only stops rendering progress. Large mazes take more animation steps. The CLI prints walls as # and the solution as *.
