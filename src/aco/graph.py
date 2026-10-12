class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, name):
        if name not in self.nodes:
            self.nodes[name] = []

    def add_edge(self, node_a, node_b, distance):
        self.add_node(node_a)
        self.add_node(node_b)

        self.nodes[node_a].append(node_b)
        self.nodes[node_b].append(node_a)

        self.edges[(node_a, node_b)] = {
            "distance": distance,
            "pheromone": 1.0
        }

        self.edges[(node_b, node_a)] = {
            "distance": distance,
            "pheromone": 1.0
        }

    def get_neighbors(self, node):
        return self.nodes.get(node, [])

    def get_distance(self, node_a, node_b):
        return self.edges[(node_a, node_b)]["distance"]

    def get_pheromone(self, node_a, node_b):
        return self.edges[(node_a, node_b)]["pheromone"]

    def set_pheromone(self, node_a, node_b, amount):
        self.edges[(node_a, node_b)]["pheromone"] = amount
        self.edges[(node_b, node_a)]["pheromone"] = amount