
from collections import deque

from src.aco.ant import Ant


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
        exploration_rate=0.10,
        reinforcement_top_k=1,
    ):
        if num_ants < 1:
            raise ValueError("num_ants must be at least 1.")
        if not 0.0 <= evaporation_rate <= 1.0:
            raise ValueError("evaporation_rate must be between 0 and 1.")
        if reinforcement_top_k < 1:
            raise ValueError("reinforcement_top_k must be at least 1.")
        if not 0.0 <= exploration_rate <= 1.0:
            raise ValueError("exploration_rate must be between 0 and 1.")

        self.graph = graph
        self.start = start
        self.destination = destination
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.pheromone_deposit = pheromone_deposit
        self.exploration_rate = exploration_rate
        self.reinforcement_top_k = reinforcement_top_k

        self.best_path = []
        self.best_distance = float("inf")
        self.goal_distances = self._calculate_goal_distances()

    def run_iteration(self):
        successful_paths = []

        # Each ant searches independently using the shared distance map.
        for _ in range(self.num_ants):
            ant = Ant(
                self.graph,
                self.start,
                self.destination,
                alpha=self.alpha,
                beta=self.beta,
                goal_distances=self.goal_distances,
                exploration_rate=self.exploration_rate,
            )

            path, distance = ant.find_path()

            if path and distance < float("inf"):
                successful_paths.append((path, distance))

                if distance < self.best_distance:
                    self.best_path = path.copy()
                    self.best_distance = distance

        # Evaporate pheromone on every edge.
        for edge in self.graph.edges:
            self.graph.edges[edge]["pheromone"] *= (
                1.0 - self.evaporation_rate
            )

        # Reinforce the top-k shortest successful paths.
        best_paths = sorted(
            successful_paths,
            key=lambda result: result[1],
        )[:self.reinforcement_top_k]

        for path, distance in best_paths:
            if distance <= 0:
                continue

            deposit = self.pheromone_deposit / distance

            for i in range(len(path) - 1):
                node_a = path[i]
                node_b = path[i + 1]

                self.graph.edges[(node_a, node_b)]["pheromone"] += deposit
                self.graph.edges[(node_b, node_a)]["pheromone"] += deposit

        # Always return a list, including when no ant finds a route.
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
