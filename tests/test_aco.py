import unittest

from src.aco.graph import Graph
from src.aco.ant import Ant
from src.aco.colony import Colony


class TestACO(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

        self.graph.add_edge("A", "B", 10)
        self.graph.add_edge("A", "C", 15)
        self.graph.add_edge("B", "C", 12)
        self.graph.add_edge("B", "D", 8)
        self.graph.add_edge("C", "D", 5)

    def test_ant_finds_valid_path(self):
        ant = Ant(self.graph, "A", "D")

        path, distance = ant.find_path()

        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "D")
        self.assertEqual(
            distance,
            sum(
                self.graph.get_distance(path[i], path[i + 1])
                for i in range(len(path) - 1)
            ),
        )

    def test_colony_finds_shortest_path(self):
        colony = Colony(
            self.graph,
            "A",
            "D",
            num_ants=20,
        )

        for _ in range(20):
            colony.run_iteration()

        self.assertEqual(colony.best_path, ["A", "B", "D"])
        self.assertEqual(colony.best_distance, 18)

    def test_pheromones_change_after_iteration(self):
        colony = Colony(self.graph, "A", "D")

        initial_pheromone = self.graph.get_pheromone("A", "B")

        colony.run_iteration()

        updated_pheromone = self.graph.get_pheromone("A", "B")

        self.assertNotEqual(initial_pheromone, updated_pheromone)

    def test_unreachable_destination(self):
        graph = Graph()
        graph.add_edge("A", "B", 5)
        graph.add_node("C")

        ant = Ant(graph, "A", "C")
        path, distance = ant.find_path()

        self.assertEqual(path, [])
        self.assertEqual(distance, float("inf"))


if __name__ == "__main__":
    unittest.main()