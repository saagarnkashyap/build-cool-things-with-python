"""Independent BFS and DFS implementations on a rectangular, unweighted maze."""

from collections import deque
from dataclasses import dataclass
import random

Cell = tuple[int, int]
PREDEFINED = """###########
#S.......E#
#.#######.#
#.........#
###########"""


@dataclass(frozen=True)
class Maze:
    rows: tuple[str, ...]
    start: Cell
    goal: Cell

    def neighbors(self, cell: Cell) -> list[Cell]:
        row, column = cell
        candidates = [(row + 1, column), (row, column + 1), (row - 1, column), (row, column - 1)]
        return [(r, c) for r, c in candidates
                if 0 <= r < len(self.rows) and 0 <= c < len(self.rows[0]) and self.rows[r][c] != "#"]


@dataclass
class SearchResult:
    explored: list[Cell]
    path: list[Cell]

    @property
    def path_length(self) -> int | None:
        return len(self.path) - 1 if self.path else None


def parse_maze(text: str) -> Maze:
    rows = tuple(text.strip("\n\r").splitlines())
    if not rows or not rows[0] or len(rows) > 61 or len(rows[0]) > 61:
        raise ValueError("Use a nonempty maze no larger than 61 x 61.")
    if any(len(row) != len(rows[0]) or set(row) - set("#.SE") for row in rows):
        raise ValueError("Use equal-width rows containing only #, ., S, and E.")
    starts = [(r, c) for r, row in enumerate(rows) for c, value in enumerate(row) if value == "S"]
    goals = [(r, c) for r, row in enumerate(rows) for c, value in enumerate(row) if value == "E"]
    if len(starts) != 1 or len(goals) != 1:
        raise ValueError("Include exactly one S and one E.")
    return Maze(rows, starts[0], goals[0])


def reconstruct(parents: dict[Cell, Cell | None], goal: Cell) -> list[Cell]:
    if goal not in parents:
        return []
    path = []
    current: Cell | None = goal
    while current is not None:
        path.append(current)
        current = parents[current]
    return list(reversed(path))


def bfs(maze: Maze) -> SearchResult:
    """A FIFO queue explores all distance-k cells before distance-(k+1) cells."""
    frontier = deque([maze.start])
    parents = {maze.start: None}
    explored = []
    while frontier:
        current = frontier.popleft()
        explored.append(current)
        if current == maze.goal:
            return SearchResult(explored, reconstruct(parents, maze.goal))
        for neighbor in maze.neighbors(current):
            if neighbor not in parents:
                parents[neighbor] = current
                frontier.append(neighbor)
    return SearchResult(explored, [])


def dfs(maze: Maze) -> SearchResult:
    """A LIFO stack commits to a branch; its first solution need not be shortest."""
    frontier = [(maze.start, None)]
    parents = {}
    explored = []
    while frontier:
        current, parent = frontier.pop()
        if current in parents:
            continue
        parents[current] = parent
        explored.append(current)
        if current == maze.goal:
            return SearchResult(explored, reconstruct(parents, maze.goal))
        for neighbor in reversed(maze.neighbors(current)):
            if neighbor not in parents:
                frontier.append((neighbor, current))
    return SearchResult(explored, [])


def generate_maze(height: int = 21, width: int = 31, seed: int | None = None) -> Maze:
    if not (5 <= height <= 61 and 5 <= width <= 61 and height % 2 and width % 2):
        raise ValueError("Height and width must be odd numbers from 5 to 61.")
    rng = random.Random(seed)
    grid = [["#"] * width for _ in range(height)]
    grid[1][1] = "."
    stack = [(1, 1)]
    while stack:
        row, column = stack[-1]
        choices = [(r, c) for r, c in ((row + 2, column), (row, column + 2), (row - 2, column), (row, column - 2))
                   if 1 <= r < height - 1 and 1 <= c < width - 1 and grid[r][c] == "#"]
        if not choices:
            stack.pop()
            continue
        r, c = rng.choice(choices)
        grid[(row + r) // 2][(column + c) // 2] = "."
        grid[r][c] = "."
        stack.append((r, c))
    grid[1][1], grid[-2][-2] = "S", "E"
    return parse_maze("\n".join("".join(row) for row in grid))


def text_solution(maze: Maze, result: SearchResult) -> str:
    path = set(result.path) - {maze.start, maze.goal}
    return "\n".join("".join("*" if (r, c) in path else value for c, value in enumerate(row))
                     for r, row in enumerate(maze.rows))
