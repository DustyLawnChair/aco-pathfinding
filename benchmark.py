
import csv
import random
from statistics import mean

from src.aco.colony import Colony
from src.aco.grid_world import build_grid, find_shortest_path


NUM_GRIDS = 20
GENERATION_CHECKPOINTS = [100, 200, 300]
NUM_ANTS = 10
BASE_SEED = 1000
OBSTACLE_RATE = 0.22

CONFIGURATION = {
    "exploration_rate": 0.10,
    "reinforcement_top_k": 1,
}


def run_trial(seed):
    graph, positions, start, destination, obstacles = build_grid(
        obstacle_rate=OBSTACLE_RATE,
        seed=seed,
    )

    bfs_path = find_shortest_path(graph, start, destination)
    bfs_distance = len(bfs_path) - 1

    # Keep the same random stream for this seed throughout all checkpoints.
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

    for generation in range(1, max(GENERATION_CHECKPOINTS) + 1):
        colony.run_iteration()
        best_history.append(colony.best_distance)

        if generation not in GENERATION_CHECKPOINTS:
            continue

        aco_distance = colony.best_distance
        found_path = aco_distance < float("inf")

        if found_path:
            gap = (
                (aco_distance - bfs_distance) / bfs_distance * 100
                if bfs_distance > 0
                else 0.0
            )
            optimal = aco_distance == bfs_distance

            first_final_best = next(
                (
                    i for i, distance in enumerate(best_history, start=1)
                    if distance == aco_distance
                ),
                None,
            )
        else:
            gap = None
            optimal = False
            first_final_best = None

        results.append({
            "seed": seed,
            "generation_checkpoint": generation,
            "obstacles": len(obstacles),
            "bfs_steps": bfs_distance,
            "aco_steps": aco_distance if found_path else None,
            "gap_percent": round(gap, 2) if gap is not None else None,
            "optimal": optimal,
            "first_generation_at_checkpoint_best": first_final_best,
        })

    return results


def summarize(checkpoint, results):
    successful = [r for r in results if r["aco_steps"] is not None]

    if not successful:
        print(f"\n{checkpoint} generations: no successful paths")
        return

    print(f"\n{checkpoint} GENERATIONS")
    print("-" * 45)
    print(f"Successful paths: {len(successful)}/{len(results)}")
    print(
        f"Optimality hit rate: "
        f"{sum(r['optimal'] for r in results) / len(results) * 100:.1f}%"
    )
    print(
        f"Average ACO distance: "
        f"{mean(r['aco_steps'] for r in successful):.2f}"
    )
    print(
        f"Average BFS distance: "
        f"{mean(r['bfs_steps'] for r in results):.2f}"
    )
    print(
        f"Average optimality gap: "
        f"{mean(r['gap_percent'] for r in successful):.2f}%"
    )


def main():
    all_results = []

    print("ACO GENERATION CHECKPOINT EXPERIMENT")
    print(f"Grids: {NUM_GRIDS}")
    print(f"Checkpoints: {GENERATION_CHECKPOINTS}")
    print(f"Ants per generation: {NUM_ANTS}")
    print(f"Exploration rate: {CONFIGURATION['exploration_rate']:.0%}")
    print(f"Top-k reinforcement: {CONFIGURATION['reinforcement_top_k']}")

    for trial in range(NUM_GRIDS):
        seed = BASE_SEED + trial
        trial_results = run_trial(seed)
        all_results.extend(trial_results)

        print(f"\nSeed {seed}")
        for result in trial_results:
            aco = (
                str(result["aco_steps"])
                if result["aco_steps"] is not None
                else "No path"
            )
            gap = (
                f"{result['gap_percent']:.2f}%"
                if result["gap_percent"] is not None
                else "N/A"
            )
            print(
                f"  Gen {result['generation_checkpoint']:3} | "
                f"ACO {aco:>7} | BFS {result['bfs_steps']:3} | "
                f"Gap {gap}"
            )

    for checkpoint in GENERATION_CHECKPOINTS:
        checkpoint_results = [
            r for r in all_results
            if r["generation_checkpoint"] == checkpoint
        ]
        summarize(checkpoint, checkpoint_results)

    output_file = "benchmark_generation_comparison.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nDetailed results saved to {output_file}")


if __name__ == "__main__":
    main()
