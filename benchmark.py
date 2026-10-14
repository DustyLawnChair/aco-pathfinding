
import csv
import random
import time
from statistics import mean

from src.aco.colony import Colony
from src.aco.grid_world import build_grid, find_shortest_path
from src.algorithms.bfs import run_bfs
from src.algorithms.astar import run_astar


# Reproducible experiment settings
NUM_GRIDS = 20
GENERATION_CHECKPOINTS = [100, 200, 300]
NUM_ANTS = 10
BASE_SEED = 1000
OBSTACLE_RATE = 0.22

CONFIGURATION = {
    "exploration_rate": 0.10,
    "reinforcement_top_k": 1,
}

OUTPUT_FILE = "benchmark_final_results.csv"


def run_trial(seed):
    """Compare BFS, A*, and ACO on the same generated grid."""
    graph, positions, start, destination, obstacles = build_grid(
        obstacle_rate=OBSTACLE_RATE,
        seed=seed,
    )

    # Time BFS independently.
    start_time = time.perf_counter()
    bfs_result = run_bfs(graph, start, destination)
    bfs_time = time.perf_counter() - start_time

    # Time A* independently.
    start_time = time.perf_counter()
    astar_result = run_astar(graph, start, destination)
    astar_time = time.perf_counter() - start_time

    # Keep the legacy BFS helper as a cross-check.
    bfs_path = find_shortest_path(graph, start, destination)
    bfs_distance = len(bfs_path) - 1 if bfs_path else float("inf")

    if bfs_result.distance != bfs_distance:
        raise AssertionError(
            f"BFS distance mismatch on seed {seed}: "
            f"{bfs_result.distance} != {bfs_distance}"
        )

    if astar_result.distance != bfs_result.distance:
        raise AssertionError(
            f"A* did not match BFS on seed {seed}: "
            f"{astar_result.distance} != {bfs_result.distance}"
        )

    # ACO gets its own reproducible random stream for this seed.
    random.seed(seed)
    colony = Colony(
        graph,
        start,
        destination,
        num_ants=NUM_ANTS,
        exploration_rate=CONFIGURATION["exploration_rate"],
        reinforcement_top_k=CONFIGURATION["reinforcement_top_k"],
    )

    results = []
    best_history = []

    aco_start_time = time.perf_counter()

    for generation in range(1, max(GENERATION_CHECKPOINTS) + 1):
        colony.run_iteration()
        best_history.append(colony.best_distance)

        if generation not in GENERATION_CHECKPOINTS:
            continue

        elapsed_aco_time = time.perf_counter() - aco_start_time
        aco_distance = colony.best_distance
        found_path = aco_distance < float("inf")

        if found_path and bfs_result.distance > 0:
            gap = (
                (aco_distance - bfs_result.distance)
                / bfs_result.distance
                * 100
            )
        else:
            gap = None

        first_final_best = (
            next(
                (
                    i
                    for i, distance in enumerate(best_history, start=1)
                    if distance == aco_distance
                ),
                None,
            )
            if found_path
            else None
        )

        results.append({
            "seed": seed,
            "generation_checkpoint": generation,
            "obstacles": len(obstacles),
            "bfs_steps": bfs_result.distance,
            "bfs_nodes_explored": bfs_result.nodes_explored,
            "bfs_time_ms": round(bfs_time * 1000, 4),
            "astar_steps": astar_result.distance,
            "astar_nodes_explored": astar_result.nodes_explored,
            "astar_time_ms": round(astar_time * 1000, 4),
            "aco_steps": aco_distance if found_path else None,
            "aco_time_ms": round(elapsed_aco_time * 1000, 4),
            "aco_nodes_explored": None,
            "gap_percent": round(gap, 2) if gap is not None else None,
            "optimal": (
                aco_distance == bfs_result.distance if found_path else False
            ),
            "first_generation_at_checkpoint_best": first_final_best,
        })

    return results


def summarize(checkpoint, results):
    """Print aggregate path-quality and runtime metrics."""
    successful = [r for r in results if r["aco_steps"] is not None]

    print(f"\n{'=' * 55}")
    print(f"RESULTS AT GENERATION {checkpoint}")
    print("=" * 55)
    print(f"Grids evaluated: {len(results)}")
    print(f"ACO successful paths: {len(successful)}/{len(results)}")

    if not successful:
        print("ACO did not find a path on any grid.")
        return

    optimal_count = sum(r["optimal"] for r in results)

    print(
        f"ACO optimality hit rate: "
        f"{optimal_count / len(results) * 100:.1f}%"
    )
    print(
        f"Average BFS distance: "
        f"{mean(r['bfs_steps'] for r in results):.2f}"
    )
    print(
        f"Average A* distance: "
        f"{mean(r['astar_steps'] for r in results):.2f}"
    )
    print(
        f"Average ACO distance: "
        f"{mean(r['aco_steps'] for r in successful):.2f}"
    )
    print(
        f"Average ACO optimality gap: "
        f"{mean(r['gap_percent'] for r in successful if r['gap_percent'] is not None):.2f}%"
    )
    print(
        f"Average BFS runtime: "
        f"{mean(r['bfs_time_ms'] for r in results):.4f} ms"
    )
    print(
        f"Average A* runtime: "
        f"{mean(r['astar_time_ms'] for r in results):.4f} ms"
    )
    print(
        f"Average ACO elapsed runtime: "
        f"{mean(r['aco_time_ms'] for r in results):.2f} ms"
    )
    print(
        f"Average BFS nodes explored: "
        f"{mean(r['bfs_nodes_explored'] for r in results):.2f}"
    )
    print(
        f"Average A* nodes explored: "
        f"{mean(r['astar_nodes_explored'] for r in results):.2f}"
    )


def main():
    all_results = []

    print("ACO / BFS / A* BENCHMARK")
    print(f"Grids: {NUM_GRIDS}")
    print(f"Seeds: {BASE_SEED}–{BASE_SEED + NUM_GRIDS - 1}")
    print(f"Generation checkpoints: {GENERATION_CHECKPOINTS}")
    print(f"Ants per generation: {NUM_ANTS}")
    print(f"Exploration rate: {CONFIGURATION['exploration_rate']:.0%}")
    print(f"Top-k reinforcement: {CONFIGURATION['reinforcement_top_k']}")

    for trial in range(NUM_GRIDS):
        seed = BASE_SEED + trial
        trial_results = run_trial(seed)
        all_results.extend(trial_results)

        print(f"Completed grid seed {seed}")

    for checkpoint in GENERATION_CHECKPOINTS:
        checkpoint_results = [
            r for r in all_results
            if r["generation_checkpoint"] == checkpoint
        ]
        summarize(checkpoint, checkpoint_results)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=all_results[0].keys(),
        )
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nDetailed results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
