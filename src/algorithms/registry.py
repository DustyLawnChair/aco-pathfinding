
from src.algorithms.bfs import run_bfs
from src.algorithms.astar import run_astar

ALGORITHMS = {
    "BFS": {
        "function": run_bfs,
        "description": "Breadth-First Search - finds a path with the fewest edges.",
    },
    "A*": {
        "function": run_astar,
        "description": "A* Search - uses path cost and a heuristic.",
    },
}
