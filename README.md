
# ACO Pathfinding

A Python pathfinding project that visualizes **Ant Colony Optimization (ACO)** and compares its results with Breadth-First Search (BFS) and A*.

The project explores heuristic search, graph theory, probabilistic decision-making, pheromone reinforcement, and algorithm performance through a visual grid environment.

## Features

- **Ant Colony Optimization:** Simulates artificial ants searching for paths using pheromone trails and probabilistic decisions.
- **Breadth-First Search:** Provides an optimal-path reference for the unweighted grid.
- **A* Search:** Uses Manhattan distance as a heuristic to guide pathfinding.
- **Interactive visualization:** Displays the grid, obstacles, ants, pheromone trails, explored nodes, and best path.
- **Benchmarking:** Evaluates ACO across reproducible grid seeds and compares path quality against BFS and A*.
- **Automated tests:** Tests core ACO behavior and grid-world pathfinding.

## Requirements

- Python 3.10 or newer
- Pygame 2.6.1

## Installation

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/DustyLawnChair/aco-pathfinding.git
cd aco-pathfinding
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Project

Launch the interactive visualizer:

```powershell
python visualizer.py
```

Run the small graph-based ACO demonstration:

```powershell
python main.py
```

## Visualizer Controls

| Key | Action |
|---|---|
| `B` | Run Breadth-First Search |
| `T` | Run A* |
| `A` | Restart ACO |
| `R` | Generate a new grid |
| `Space` | Pause or resume |
| `1` / `2` / `3` | Change generation limits |
| `+` / `-` | Adjust simulation speed |
| `F` | Fast-forward |
| `0` | Reset speed |
| `Esc` | Quit |

## Algorithms

### Ant Colony Optimization (ACO)

ACO is a population-based metaheuristic inspired by the foraging behavior of ants. Artificial ants construct candidate paths, and successful paths reinforce their edges with virtual pheromones. Pheromone evaporation reduces older trail strength, balancing exploitation of promising routes with exploration of alternatives.

ACO is stochastic and does not guarantee an optimal path.

### Breadth-First Search (BFS)

BFS explores a graph level by level. On an unweighted grid, it finds a shortest path when one exists. This project uses BFS as an optimal-distance reference for evaluating ACO.

### A* Search

A* prioritizes nodes using the sum of the cost so far and a heuristic estimate of the remaining distance. This project uses Manhattan distance, appropriate for four-directional grid movement.

## Benchmark Methodology

The benchmark uses:

- 20 deterministic grid seeds: `1000–1019`
- Obstacle rate: `22%`
- 10 ants per generation
- Baseline exploration rate: `10%`
- Top-1 path reinforcement
- Generation checkpoints: `100`, `200`, and `300`

ACO's best path is evaluated against BFS's shortest-path distance. The optimality hit rate is the percentage of tested grids where ACO matches that distance. The optimality gap measures how much longer the ACO path is than the BFS reference.

Run the benchmark:

```powershell
python benchmark.py
```

The runner writes detailed results to `benchmark_final_results.csv`. It reports path lengths, nodes explored for BFS and A*, elapsed runtime, and ACO path quality at each checkpoint.

## Benchmark Results

Baseline results across 20 grids on one benchmark run:

| Metric | 100 Generations | 200 Generations | 300 Generations |
|---|---:|---:|---:|
| Successful ACO paths | 20/20 | 20/20 | 20/20 |
| Optimality hit rate | 30% | 40% | 75% |
| Average ACO path length | 41.90 | 40.10 | 38.60 |
| Average optimality gap | 10.00% | 5.26% | 1.31% |
| Average cumulative ACO runtime | 101.96 ms | 214.40 ms | 325.87 ms |

At 300 generations, ACO matched the BFS-optimal path length on 15 of the 20 grids. The results show that additional generations improved path quality for this configuration and sample.

BFS explored an average of 309.10 nodes per grid, while A* explored 202.55. Both algorithms returned the same average path distance of 38.10.

Runtime values are specific to the machine and run environment. These results are an experiment over 20 grids, not a guarantee of performance on every map.

## Tests

Run the unit tests with:

```powershell
python -m unittest discover -s tests -v
```

## Project Structure

```text
aco-pathfinding/
├── src/
│   ├── aco/
│   │   ├── ant.py
│   │   ├── colony.py
│   │   ├── graph.py
│   │   └── grid_world.py
│   └── algorithms/
│       ├── astar.py
│       ├── base.py
│       ├── bfs.py
│       └── registry.py
├── tests/
├── benchmark.py
├── benchmark_final_results.csv
├── benchmark_results.csv
├── benchmark_comparison.csv
├── benchmark_generation_comparison.csv
├── main.py
├── visualizer.py
├── requirements.txt
└── README.md
```

## Future Improvements

- Repeat ACO experiments with multiple independent random streams per grid.
- Compare additional colony configurations using the same benchmark methodology.
- Visualize benchmark summaries and convergence statistics.
- Expand tests for unreachable grids and algorithm edge cases.
