
import random
from collections import deque


class Ant:
    def __init__(self, graph, start, destination, alpha=1.0, beta=2.0):
        self.graph = graph
        self.start = start
        self.destination = destination
        self.alpha = alpha
        self.beta = beta
        self.goal_distances = self._calculate_goal_distances()

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
            pheromone = self.graph.get_pheromone(current, neighbor)

            if neighbor in self.goal_distances:
                # Shortest remaining distance through the graph.
                heuristic = 1.0 / (1.0 + self.goal_distances[neighbor])
            else:
                # Keep unreachable branches possible, but strongly disfavored.
                heuristic = 1e-6

            weight = pheromone ** self.alpha * heuristic ** self.beta
            weights.append(weight)

        return random.choices(candidates, weights=weights, k=1)[0]

    
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

