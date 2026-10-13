
from collections import deque

from src.algorithms.base import PathfindingResult


def run_bfs(graph, start, destination):
    queue = deque([start])
    parent = {start: None}
    nodes_explored = 0

    while queue:
        current = queue.popleft()
        nodes_explored += 1

        if current == destination:
            break

        for neighbor in graph.get_neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    if destination not in parent:
        return PathfindingResult(
            path=[],
            distance=float("inf"),
            nodes_explored=nodes_explored,
            algorithm="BFS",
        )

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()

    distance = sum(
        graph.get_distance(path[i], path[i + 1])
        for i in range(len(path) - 1)
    )

    return PathfindingResult(
        path=path,
        distance=distance,
        nodes_explored=nodes_explored,
        algorithm="BFS",
    )
