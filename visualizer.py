import math
import pygame

from src.aco.grid_world import build_grid, find_shortest_path
from src.aco.colony import Colony

WIDTH, HEIGHT = 900, 950
FPS = 60
ROWS, COLS = 20, 20
CELL_SIZE = 30

GRID_X = (WIDTH - COLS * CELL_SIZE) // 2
GRID_Y = 65

BACKGROUND = (18, 20, 30)
OPEN_COLOR = (32, 36, 49)
WALL_COLOR = (9, 11, 18)
GRID_COLOR = (49, 55, 72)
TEXT_COLOR = (225, 230, 240)
START_COLOR = (80, 240, 150)
DESTINATION_COLOR = (255, 100, 110)
PATH_COLOR = (90, 160, 255)
ANT_COLOR = (255, 175, 65)
WEAK_COLOR = (65, 85, 150)
STRONG_COLOR = (80, 240, 150)

ANT_SPEED = 180
SPEED_MULTIPLIER = 1.0
MIN_SPEED = 0.25
MAX_SPEED = 8.0
SPEED_STEP = 0.5

GRAPH_X = 185
GRAPH_Y = 875
GRAPH_WIDTH = 500
GRAPH_HEIGHT = 55


def build_simulation():
    graph, positions, start, destination, obstacles = build_grid(
        rows=ROWS,
        cols=COLS,
        obstacle_rate=0.22,
    )

    colony = Colony(
        graph,
        start=start,
        destination=destination,
        num_ants=20,
        evaporation_rate=0.3,
        alpha=1.0,
        beta=2.0,
    )

    shortest_path = find_shortest_path(graph, start, destination)

    return graph, positions, start, destination, obstacles, colony, shortest_path


def cell_center(node):
    x, y = node
    return (
        GRID_X + x * CELL_SIZE + CELL_SIZE // 2,
        GRID_Y + y * CELL_SIZE + CELL_SIZE // 2,
    )


def interpolate_color(start, end, amount):
    amount = max(0.0, min(1.0, amount))
    return tuple(
        int(a + (b - a) * amount)
        for a, b in zip(start, end)
    )


def spawn_ants(colony):
    paths = colony.run_iteration()
    active_ants = []

    for path, distance in paths:
        if len(path) >= 2:
            active_ants.append({
                "path": path,
                "segment": 0,
                "progress": 0.0,
                "distance": distance,
            })

    return active_ants



def update_ants(active_ants, delta_time, speed_multiplier=1.0):
    remaining = []

    for ant in active_ants:
        path = ant["path"]
        segment = ant["segment"]

        if segment >= len(path) - 1:
            continue

        node_a = path[segment]
        node_b = path[segment + 1]

        x1, y1 = cell_center(node_a)
        x2, y2 = cell_center(node_b)
        length = math.hypot(x2 - x1, y2 - y1)

        ant["progress"] += (
            ANT_SPEED * speed_multiplier * delta_time / length
        )

        while ant["progress"] >= 1.0:
            ant["progress"] -= 1.0
            ant["segment"] += 1

            if ant["segment"] >= len(path) - 1:
                break

        if ant["segment"] < len(path) - 1:
            remaining.append(ant)

    return remaining


def draw_grid(screen, obstacles, shortest_path):
    for y in range(ROWS):
        for x in range(COLS):
            node = (x, y)
            rect = pygame.Rect(
                GRID_X + x * CELL_SIZE,
                GRID_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            color = WALL_COLOR if node in obstacles else OPEN_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    # Show the optimal path found by breadth-first search.
    for node in shortest_path:
        rect = pygame.Rect(
            GRID_X + node[0] * CELL_SIZE + 10,
            GRID_Y + node[1] * CELL_SIZE + 10,
            CELL_SIZE - 20,
            CELL_SIZE - 20,
        )
        pygame.draw.rect(screen, PATH_COLOR, rect, border_radius=3)

    start_rect = pygame.Rect(
        GRID_X + 2,
        GRID_Y + 2,
        CELL_SIZE - 4,
        CELL_SIZE - 4,
    )
    pygame.draw.rect(screen, START_COLOR, start_rect, border_radius=5)

    destination_rect = pygame.Rect(
        GRID_X + (COLS - 1) * CELL_SIZE + 2,
        GRID_Y + (ROWS - 1) * CELL_SIZE + 2,
        CELL_SIZE - 4,
        CELL_SIZE - 4,
    )
    pygame.draw.rect(
        screen, DESTINATION_COLOR, destination_rect, border_radius=5
    )


def draw_pheromones(screen, graph):
    max_pheromone = max(
        (data["pheromone"] for data in graph.edges.values()),
        default=1.0,
    )
    max_pheromone = max(max_pheromone, 0.001)

    for (node_a, node_b), data in graph.edges.items():
        # Draw each undirected connection only once.
        if node_a > node_b:
            continue

        strength = data["pheromone"] / max_pheromone
        color = interpolate_color(WEAK_COLOR, STRONG_COLOR, strength)

        pygame.draw.line(
            screen,
            color,
            cell_center(node_a),
            cell_center(node_b),
            max(1, min(5, int(strength * 5))),
        )

def draw_best_path(screen, best_path):
    if len(best_path) < 2:
        return

    points = [cell_center(node) for node in best_path]

    pygame.draw.lines(
        screen,
        (60, 255, 145),
        False,
        points,
        4,
    )

def draw_ants(screen, active_ants):
    for index, ant in enumerate(active_ants):
        path = ant["path"]
        segment = ant["segment"]

        if segment >= len(path) - 1:
            continue

        x1, y1 = cell_center(path[segment])
        x2, y2 = cell_center(path[segment + 1])
        progress = ant["progress"]

        x = x1 + (x2 - x1) * progress
        y = y1 + (y2 - y1) * progress

        # Spread overlapping ants slightly around their position.
        angle = index * 2.399963
        offset_x = math.cos(angle) * 6
        offset_y = math.sin(angle) * 6

        position = (int(x + offset_x), int(y + offset_y))

        pygame.draw.circle(screen, (20, 22, 30), position, 5)
        pygame.draw.circle(screen, ANT_COLOR, position, 4)

def draw_convergence_graph(screen, history):
    if len(history) < 2:
        return

    graph_rect = pygame.Rect(
        GRAPH_X, GRAPH_Y, GRAPH_WIDTH, GRAPH_HEIGHT
    )

    pygame.draw.rect(screen, (25, 28, 40), graph_rect)
    pygame.draw.rect(screen, GRID_COLOR, graph_rect, 1)

    graph_title = pygame.font.Font(None, 20).render(
        "ACO Convergence (best-ever path length in grid steps)",
        True,
        TEXT_COLOR,
    )
    screen.blit(graph_title, (GRAPH_X, GRAPH_Y - 22))

    valid_distances = [
        distance for distance in history
        if math.isfinite(distance)
    ]

    if len(valid_distances) < 2:
        return

    minimum = min(valid_distances)
    maximum = max(valid_distances)

    # Avoid dividing by zero when all recorded distances are equal.
    if maximum == minimum:
        maximum += 1

    points = []

    for index, distance in enumerate(history):
        if not math.isfinite(distance):
            continue

        x = GRAPH_X + index / max(len(history) - 1, 1) * GRAPH_WIDTH
        y = GRAPH_Y + GRAPH_HEIGHT - (
            (distance - minimum) / (maximum - minimum) * GRAPH_HEIGHT
        )

        points.append((int(x), int(y)))

    if len(points) >= 2:
        pygame.draw.lines(
            screen,
            STRONG_COLOR,
            False,
            points,
            2,
        )

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ant Colony Optimization - Pathfinding")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 23)
    small_font = pygame.font.Font(None, 19)

    def reset_simulation():
        graph, positions, start, destination, obstacles, colony, shortest_path = (
            build_simulation()
        )
        ants = spawn_ants(colony)
        return graph, obstacles, colony, shortest_path, ants, 1

    graph, obstacles, colony, shortest_path, active_ants, generation = (
        reset_simulation()
    )

    paused = False
    running = True
    generation_limit = 100
    simulation_complete = False
    speed_multiplier = 1.0
    fast_forward = False

    best_distance_history = []

    while running:
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    graph, obstacles, colony, shortest_path, active_ants, generation = (
                        reset_simulation()
                    )
                    best_distance_history = []
                elif event.key == pygame.K_1:
                    generation_limit = 100
                    simulation_complete = False
                elif event.key == pygame.K_2:
                    generation_limit = 200
                    simulation_complete = False
                elif event.key == pygame.K_3:
                    generation_limit = 300
                    simulation_complete = False
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    speed_multiplier = min(MAX_SPEED, speed_multiplier + SPEED_STEP)

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed_multiplier = max(MIN_SPEED, speed_multiplier - SPEED_STEP)

                elif event.key == pygame.K_0:
                    speed_multiplier = 1.0

                elif event.key == pygame.K_f:
                    fast_forward = not fast_forward




        if not paused and not simulation_complete:
            if fast_forward:
                active_ants = []

            else:
                active_ants = update_ants(
                    active_ants,
                    delta_time,
                    speed_multiplier,
                )

            if not active_ants:
                if generation >= generation_limit:
                    simulation_complete = True
                else:
                    active_ants = spawn_ants(colony)
                    generation += 1
                    best_distance_history.append(colony.best_distance)

        screen.fill(BACKGROUND)

        title = font.render(
            "ANT COLONY OPTIMIZATION | GRID PATHFINDING",
            True,
            TEXT_COLOR,
        )
        screen.blit(title, (GRID_X, 25))

        draw_grid(screen, obstacles, shortest_path)
        draw_pheromones(screen, graph)
        draw_best_path(screen, colony.best_path)
        draw_ants(screen, active_ants)
        draw_convergence_graph(screen, best_distance_history)
        best = (
            f"{colony.best_distance:.0f} steps"
            if math.isfinite(colony.best_distance)
            else "Not found yet"
        )
        optimal = (
            f"{len(shortest_path) - 1} steps"
            if shortest_path
            else "Unavailable"
        )

        if shortest_path and math.isfinite(colony.best_distance):
            optimal_distance = len(shortest_path) - 1
            optimality_gap = (
                (colony.best_distance - optimal_distance)
                / optimal_distance
            ) * 100
            gap_text = f"{optimality_gap:.1f}%"
        else:
            gap_text = "Unavailable"



        status_lines = [
            f"Generation: {generation}/{generation_limit}    Active ants: {len(active_ants)}",
            f"Best ACO distance: {best}    BFS optimal distance: {optimal}",
            f"Optimality gap: {gap_text}",
            f"Obstacles: {len(obstacles)}",
            "Search limit: 1 = 100 gens    2 = 200 gens    3 = 300 gens",
            f"Speed: {speed_multiplier:.1f}x    Fast-forward: {'ON' if fast_forward else 'OFF'}",
            "+/-: speed    0: reset speed    F: fast-forward",
            "SPACE: pause/resume    R: new grid    ESC: quit",
        ]

        for index, line in enumerate(status_lines):
            rendered = small_font.render(line, True, TEXT_COLOR)
            screen.blit(rendered, (GRID_X, 690 + index * 21))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()