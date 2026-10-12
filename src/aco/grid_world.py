import random
from collections import deque

from src.aco.graph import Graph


def build_grid(rows=20, cols=20, obstacle_rate=0.22, seed=None):
    """
    Generate a grid graph with random obstacles.

    Returns:
        graph: Graph containing all open cells and their connections
        positions: Maps each node to its (x, y) grid coordinates
        start: Starting node
        destination: Destination node
        obstacles: Set of blocked grid coordinates
    """
    rng = random.Random(seed)

    start = (0, 0)
    destination = (cols - 1, rows - 1)

    for _ in range(100):
        obstacles = {
            (x, y)
            for y in range(rows)
            for x in range(cols)
            if (x, y) not in (start, destination)
            and rng.random() < obstacle_rate
        }

        positions = {
            (x, y): (x, y)
            for y in range(rows)
            for x in range(cols)
            if (x, y) not in obstacles
        }

        graph = Graph()

        # Add every open cell, including isolated cells.
        for node in positions:
            graph.add_node(node)

        # Connect orthogonal neighbors.
        for x, y in positions:
            for neighbor in (
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            ):
                if neighbor in positions:
                    graph.add_edge(node_a=(x, y), node_b=neighbor, distance=1)

        shortest_path = find_shortest_path(
            graph, start, destination
        )

        # Retry if the obstacles disconnect start and destination.
        if shortest_path:
            return graph, positions, start, destination, obstacles

    raise RuntimeError(
        "Could not generate a connected grid. "
        "Try reducing obstacle_rate."
    )


def find_shortest_path(graph, start, destination):
    """Find an optimal path using breadth-first search."""
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        current, path = queue.popleft()

        if current == destination:
            return path

        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []