from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from maze import PREDEFINED, bfs, dfs, generate_maze, parse_maze


class MazeTests(unittest.TestCase):
    def assert_valid_path(self, maze, result):
        self.assertEqual(result.path[0], maze.start)
        self.assertEqual(result.path[-1], maze.goal)
        for before, after in zip(result.path, result.path[1:]):
            self.assertIn(after, maze.neighbors(before))
        self.assertEqual(len(result.explored), len(set(result.explored)))

    def test_bfs_shortest_and_dfs_counterexample(self):
        maze = parse_maze(PREDEFINED)
        breadth, depth = bfs(maze), dfs(maze)
        self.assertEqual(breadth.path_length, 8)
        self.assertEqual(depth.path_length, 12)
        self.assert_valid_path(maze, breadth)
        self.assert_valid_path(maze, depth)

    def test_generated_mazes_are_reproducible_and_solvable(self):
        for seed in range(6):
            maze = generate_maze(11, 15, seed)
            self.assertEqual(maze, generate_maze(11, 15, seed))
            self.assert_valid_path(maze, bfs(maze))
            self.assert_valid_path(maze, dfs(maze))

    def test_unreachable_goal(self):
        maze = parse_maze("#####\n#S#E#\n#####")
        for search in (bfs, dfs):
            result = search(maze)
            self.assertEqual(result.path, [])
            self.assertIsNone(result.path_length)

    def test_invalid_mazes(self):
        for text in ("", "##\n#S.E#", "S..", "SS.E", "SxE"):
            with self.assertRaises(ValueError):
                parse_maze(text)

    def test_invalid_generation_sizes(self):
        for height, width in ((4, 5), (6, 7), (5, 64)):
            with self.assertRaises(ValueError):
                generate_maze(height, width)

    def test_no_wraparound_at_edges(self):
        maze = parse_maze("S.E")
        self.assertEqual(bfs(maze).path_length, 2)
        self.assertEqual(maze.neighbors((0, 0)), [(0, 1)])
