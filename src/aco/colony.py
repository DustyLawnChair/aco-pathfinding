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

        # Reinforce edges used by successful ants.
        for path, distance in successful_paths:
            deposit = self.pheromone_deposit / distance

            for i in range(len(path) - 1):
                node_a = path[i]
                node_b = path[i + 1]

                self.graph.edges[(node_a, node_b)]["pheromone"] += deposit
                self.graph.edges[(node_b, node_a)]["pheromone"] += deposit

        return successful_paths