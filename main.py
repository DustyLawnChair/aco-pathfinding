from src.aco.graph import Graph


def main():
    graph = Graph()

    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 15)
    graph.add_edge("B", "C", 12)

    print("Neighbors of A:", graph.get_neighbors("A"))
    print("Distance A -> B:", graph.get_distance("A", "B"))
    print("Pheromone A -> B:", graph.get_pheromone("A", "B"))


if __name__ == "__main__":
    main()