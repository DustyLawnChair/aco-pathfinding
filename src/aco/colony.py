from src.aco.ant import Ant
from collections import deque


class Colony:
    def __init__(
        self,
        graph,
        start,
        destination,
        num_ants=10,
        evaporation_rate=0.1,
        alpha=1.0,
        beta=2.0,
        pheromone_deposit=100.0,
    ):
        self.graph = graph
        self.start = start
        self.destination = destination
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.pheromone_deposit = pheromone_deposit

        self.best_path = []
        self.best_distance = float("inf")
        self.goal_distances = self._calculate_goal_distances()

    def run_iteration(self):
        successful_paths = []

        # Each ant independently searches for a path.
        for _ in range(self.num_ants):
            ant = Ant(
                self.graph,
                self.start,
                self.destination,
                alpha=self.alpha,
                beta=self.beta,
                goal_distances=self.goal_distances,
            )

            path, distance = ant.find_path()

            if path and distance < float("inf"):
                successful_paths.append((path, distance))

                if distance < self.best_distance:
                    self.best_path = path
                    self.best_distance = distance

        # Evaporate pheromones on all edges.
        for edge in self.graph.edges:
            self.graph.edges[edge]["pheromone"] *= (
                1.0 - self.evaporation_rate
            )

       

        # Reinforce only the best successful route this iteration.
        if successful_paths:
            best_iteration_path, best_iteration_distance = min(
                successful_paths,
                key=lambda result: result[1],
            )

            deposit = self.pheromone_deposit / best_iteration_distance

            for i in range(len(best_iteration_path) - 1):
                node_a = best_iteration_path[i]
                node_b = best_iteration_path[i + 1]

                self.graph.edges[(node_a, node_b)]["pheromone"] += deposit
                self.graph.edges[(node_b, node_a)]["pheromone"] += deposit

        # Always return a list, even if no ants find a path.
        return successful_paths


    def _calculate_goal_distances(self):
        distances = {self.destination: 0}
        queue = deque([self.destination])

        while queue:
            current = queue.popleft()

            for neighbor in self.graph.get_neighbors(current):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)

        return distances