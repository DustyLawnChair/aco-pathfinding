
import heapq
from itertools import count

from src.algorithms.base import PathfindingResult


def manhattan_distance(node_a, node_b):
    """Estimate grid distance using four-directional movement."""
    return (
        abs(node_a[0] - node_b[0])
        + abs(node_a[1] - node_b[1])
    )


def run_astar(graph, start, destination):
    """Find a shortest path using A* with Manhattan distance."""
    sequence = count()

    frontier = [
        (
            manhattan_distance(start, destination),
            next(sequence),
            start,
        )
    ]

    came_from = {start: None}
    cost_so_far = {start: 0}
    nodes_explored = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        nodes_explored += 1

        if current == destination:
            break

        for neighbor in graph.get_neighbors(current):
            new_cost = (
                cost_so_far[current]
                + graph.get_distance(current, neighbor)
            )

            if (
                neighbor not in cost_so_far
                or new_cost < cost_so_far[neighbor]
            ):
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current

                priority = (
                    new_cost
                    + manhattan_distance(neighbor, destination)
                )

                heapq.heappush(
                    frontier,
                    (priority, next(sequence), neighbor),
                )

    if destination not in came_from:
        return PathfindingResult(
            path=[],
            distance=float("inf"),
            nodes_explored=nodes_explored,
            algorithm="A*",
        )

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()

    return PathfindingResult(
        path=path,
        distance=cost_so_far[destination],
        nodes_explored=nodes_explored,
        algorithm="A*",
    )
