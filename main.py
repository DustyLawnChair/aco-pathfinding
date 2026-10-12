
from src.aco.graph import Graph
from src.aco.colony import Colony


def main():
    graph = Graph()

    # Build a small graph with multiple possible routes.
    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 15)
    graph.add_edge("B", "C", 12)
    graph.add_edge("B", "D", 8)
    graph.add_edge("C", "D", 5)

    colony = Colony(
        graph=graph,
        start="A",
        destination="D",
        num_ants=10,
        evaporation_rate=0.1,
    )

    # Run the optimization process.
    for iteration in range(1, 21):
        paths = colony.run_iteration()

        print(
            f"Iteration {iteration:02d} | "
            f"Successful ants: {len(paths)} | "
            f"Best distance: {colony.best_distance}"
        )

    print("\n--- Optimization Results ---")
    print("Best path:", " -> ".join(colony.best_path))
    print("Best distance:", colony.best_distance)

    print("\n--- Final Pheromone Levels ---")
    for (node_a, node_b), data in graph.edges.items():
        if node_a < node_b:
            print(
                f"{node_a} <-> {node_b}: "
                f"{data['pheromone']:.2f}"
            )


if __name__ == "__main__":
    main()
