
import random


class Ant:
    def __init__(self, graph, start, destination, alpha=1.0, beta=2.0):
        self.graph = graph
        self.start = start
        self.destination = destination
        self.alpha = alpha
        self.beta = beta

    def find_path(self):
        current = self.start
        path = [current]
        visited = {current}
        total_distance = 0.0

        while current != self.destination:
            candidates = [
                neighbor
                for neighbor in self.graph.get_neighbors(current)
                if neighbor not in visited
            ]

            if not candidates:
                return [], float("inf")

            next_node = self._choose_next(current, candidates)

            total_distance += self.graph.get_distance(
                current, next_node
            )

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        return path, total_distance

    def _choose_next(self, current, candidates):
        weights = []

        for neighbor in candidates:
            pheromone = self.graph.get_pheromone(
                current, neighbor
            )
            distance = self.graph.get_distance(
                current, neighbor
            )

            weight = (
                pheromone ** self.alpha
                * (1.0 / distance) ** self.beta
            )
            weights.append(weight)

        return random.choices(candidates, weights=weights, k=1)[0]
