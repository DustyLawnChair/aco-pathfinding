import unittest

from src.aco.grid_world import (
    build_grid,
    find_shortest_path,
)


class TestGridWorld(unittest.TestCase):

    def test_grid_has_valid_start_and_destination(self):
        graph, positions, start, destination, obstacles = (
            build_grid(rows=10, cols=10, seed=42)
        )

        self.assertIn(start, positions)
        self.assertIn(destination, positions)
        self.assertNotIn(start, obstacles)
        self.assertNotIn(destination, obstacles)

    def test_shortest_path_avoids_obstacles(self):
        graph, positions, start, destination, obstacles = (
            build_grid(rows=10, cols=10, seed=42)
        )

        path = find_shortest_path(graph, start, destination)

        self.assertTrue(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], destination)

        for node in path:
            self.assertNotIn(node, obstacles)

        self.assertEqual(len(path) - 1, len(path) - 1)

    def test_path_moves_between_adjacent_cells(self):
        graph, positions, start, destination, obstacles = (
            build_grid(rows=10, cols=10, seed=42)
        )

        path = find_shortest_path(graph, start, destination)

        for current, following in zip(path, path[1:]):
            self.assertEqual(
                abs(current[0] - following[0])
                + abs(current[1] - following[1]),
                1,
            )


if __name__ == "__main__":
    unittest.main()