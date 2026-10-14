import math
import time

import pygame

from src.aco.colony import Colony
from src.aco.grid_world import build_grid, find_shortest_path
from src.algorithms.registry import ALGORITHMS


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1100, 850
FPS = 60

ROWS, COLS = 20, 20
CELL_SIZE = 25
GRID_X, GRID_Y = 30, 95
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE

PANEL_X = 570
PANEL_WIDTH = WIDTH - PANEL_X - 30

BACKGROUND = (18, 20, 30)
PANEL_COLOR = (25, 29, 42)
OPEN_COLOR = (32, 36, 49)
WALL_COLOR = (9, 11, 18)
GRID_COLOR = (49, 55, 72)
TEXT_COLOR = (225, 230, 240)
MUTED_TEXT = (155, 165, 185)
START_COLOR = (80, 240, 150)
DESTINATION_COLOR = (255, 100, 110)
PATH_COLOR = (90, 160, 255)
EXPLORED_COLOR = (75, 95, 145)
ANT_COLOR = (255, 175, 65)
WEAK_COLOR = (65, 85, 150)
STRONG_COLOR = (80, 240, 150)
ACCENT_COLOR = (120, 170, 255)

ANT_SPEED = 180
MIN_SPEED = 0.25
MAX_SPEED = 8.0
SPEED_STEP = 0.5
SEARCH_NODES_PER_SECOND = 180

GRAPH_X = PANEL_X + 12
GRAPH_Y = 585
GRAPH_WIDTH = PANEL_WIDTH - 24
GRAPH_HEIGHT = 85

# Text/layout constants are centralized so future layout changes are simple.
TITLE_Y = 28
PANEL_TITLE_Y = 88
STATUS_LINE_GAP = 25


def format_duration(seconds):
    """Format seconds as HH:MM:SS, including simulated durations."""
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def build_simulation():
    """Create a grid, an ACO colony, and the BFS optimal reference path."""
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

    return {
        "graph": graph,
        "positions": positions,
        "start": start,
        "destination": destination,
        "obstacles": obstacles,
        "colony": colony,
        "shortest_path": shortest_path,
    }


def cell_center(node):
    x, y = node
    return (
        GRID_X + x * CELL_SIZE + CELL_SIZE // 2,
        GRID_Y + y * CELL_SIZE + CELL_SIZE // 2,
    )


def interpolate_color(start, end, amount):
    amount = max(0.0, min(1.0, amount))
    return tuple(
        int(first + (second - first) * amount)
        for first, second in zip(start, end)
    )


def spawn_ants(colony):
    """Run one ACO generation and return its animatable ant paths."""
    active_ants = []
    paths = colony.run_iteration()

    for path, distance in paths:
        if len(path) >= 2:
            active_ants.append({
                "path": path,
                "segment": 0,
                "progress": 0.0,
                "distance": distance,
            })

    return active_ants


def estimate_generation_duration(active_ants):
    """Estimate how long a generation's longest ant path takes at 1x speed."""
    longest_path_steps = max(
        (len(ant["path"]) - 1 for ant in active_ants),
        default=0,
    )
    return longest_path_steps * CELL_SIZE / ANT_SPEED


def update_ants(active_ants, delta_time, speed_multiplier=1.0):
    """Advance animated ants along their paths."""
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
        segment_length = max(math.hypot(x2 - x1, y2 - y1), 1.0)

        ant["progress"] += (
            ANT_SPEED * speed_multiplier * delta_time / segment_length
        )

        while ant["progress"] >= 1.0:
            ant["progress"] -= 1.0
            ant["segment"] += 1
            if ant["segment"] >= len(path) - 1:
                break

        if ant["segment"] < len(path) - 1:
            remaining.append(ant)

    return remaining


def draw_grid(
    screen,
    obstacles,
    path,
    start,
    destination,
    explored_nodes=None,
):
    """Draw grid layers in order: terrain, explored nodes, path, endpoints."""
    explored_set = set(explored_nodes or [])
    path_set = set(path or [])

    for y in range(ROWS):
        for x in range(COLS):
            node = (x, y)
            rect = pygame.Rect(
                GRID_X + x * CELL_SIZE,
                GRID_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            if node in obstacles:
                color = WALL_COLOR
            elif node in path_set:
                color = PATH_COLOR
            elif node in explored_set:
                color = EXPLORED_COLOR
            else:
                color = OPEN_COLOR

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    start_rect = pygame.Rect(
        GRID_X + start[0] * CELL_SIZE + 2,
        GRID_Y + start[1] * CELL_SIZE + 2,
        CELL_SIZE - 4,
        CELL_SIZE - 4,
    )
    pygame.draw.rect(screen, START_COLOR, start_rect, border_radius=5)

    destination_rect = pygame.Rect(
        GRID_X + destination[0] * CELL_SIZE + 2,
        GRID_Y + destination[1] * CELL_SIZE + 2,
        CELL_SIZE - 4,
        CELL_SIZE - 4,
    )
    pygame.draw.rect(
        screen,
        DESTINATION_COLOR,
        destination_rect,
        border_radius=5,
    )


def draw_pheromones(screen, graph):
    """Render pheromone intensity on graph edges."""
    max_pheromone = max(
        (data["pheromone"] for data in graph.edges.values()),
        default=1.0,
    )
    max_pheromone = max(max_pheromone, 0.001)

    for (node_a, node_b), data in graph.edges.items():
        if node_a > node_b:
            continue

        normalized = max(0.0, min(1.0, data["pheromone"] / max_pheromone))
        # Keep pheromone edges as a subtle background layer so they do not
        # visually overwhelm the ants or the best-known path.
        strength = 0.12 + normalized * 0.28
        color = interpolate_color(WEAK_COLOR, STRONG_COLOR, strength)
        pygame.draw.line(
            screen,
            color,
            cell_center(node_a),
            cell_center(node_b),
            1,
        )


def draw_best_path(screen, best_path):
    if len(best_path) < 2:
        return
    pygame.draw.lines(
        screen,
        (60, 255, 145),
        False,
        [cell_center(node) for node in best_path],
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

        angle = index * 2.399963
        position = (
            int(x + math.cos(angle) * 6),
            int(y + math.sin(angle) * 6),
        )
        pygame.draw.circle(screen, (20, 22, 30), position, 5)
        pygame.draw.circle(screen, ANT_COLOR, position, 4)


def draw_panel(screen, rect, title, font):
    pygame.draw.rect(screen, PANEL_COLOR, rect, border_radius=10)
    pygame.draw.rect(screen, GRID_COLOR, rect, width=1, border_radius=10)
    screen.blit(font.render(title, True, ACCENT_COLOR), (rect.x + 14, rect.y + 12))


def draw_lines(screen, font, lines, x, y, line_gap=STATUS_LINE_GAP):
    for index, line in enumerate(lines):
        screen.blit(
            font.render(line, True, TEXT_COLOR),
            (x, y + index * line_gap),
        )


def draw_legend(screen, font, x, y):
    """Render compact color legend for the grid."""
    items = [
        (OPEN_COLOR, "Open"),
        (WALL_COLOR, "Obstacle"),
        (EXPLORED_COLOR, "Explored"),
        (PATH_COLOR, "Final path"),
        (START_COLOR, "Start"),
        (DESTINATION_COLOR, "Goal"),
    ]

    item_width = 150
    for index, (color, label) in enumerate(items):
        column = index % 3
        row = index // 3
        item_x = x + column * item_width
        item_y = y + row * 28
        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(item_x, item_y + 2, 15, 15),
            border_radius=3,
        )
        screen.blit(font.render(label, True, TEXT_COLOR), (item_x + 23, item_y))


def draw_convergence_graph(screen, history, font):
    """Draw ACO best-distance history inside the right-hand panel."""
    graph_rect = pygame.Rect(GRAPH_X, GRAPH_Y, GRAPH_WIDTH, GRAPH_HEIGHT)
    pygame.draw.rect(screen, (19, 22, 33), graph_rect, border_radius=5)
    pygame.draw.rect(screen, GRID_COLOR, graph_rect, width=1, border_radius=5)

    valid = [
        (index, value)
        for index, value in enumerate(history)
        if math.isfinite(value)
    ]
    if len(valid) < 2:
        message = "Convergence data appears as generations complete."
        screen.blit(font.render(message, True, MUTED_TEXT), (GRAPH_X + 10, GRAPH_Y + 12))
        return

    values = [value for _, value in valid]
    minimum, maximum = min(values), max(values)
    if maximum == minimum:
        maximum += 1

    points = []
    for index, distance in valid:
        x = GRAPH_X + index / max(len(history) - 1, 1) * GRAPH_WIDTH
        y = GRAPH_Y + GRAPH_HEIGHT - (
            (distance - minimum) / (maximum - minimum) * (GRAPH_HEIGHT - 12)
        ) - 6
        points.append((int(x), int(y)))

    if len(points) >= 2:
        pygame.draw.lines(screen, STRONG_COLOR, False, points, 2)


def create_algorithm_result(name, state):
    return ALGORITHMS[name]["function"](
        state["graph"],
        state["start"],
        state["destination"],
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ACO | Grid Pathfinding")

    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 31)
    panel_font = pygame.font.Font(None, 23)
    body_font = pygame.font.Font(None, 18)
    small_font = pygame.font.Font(None, 17)

    grid_panel = pygame.Rect(18, 70, GRID_WIDTH + 24, GRID_HEIGHT + 42)
    metrics_panel = pygame.Rect(PANEL_X, 70, PANEL_WIDTH, 300)
    controls_panel = pygame.Rect(PANEL_X, 385, PANEL_WIDTH, 160)
    graph_panel = pygame.Rect(PANEL_X, 560, PANEL_WIDTH, 140)
    legend_panel = pygame.Rect(PANEL_X, 710, PANEL_WIDTH, 95)

    def reset_state():
        state = build_simulation()
        state["active_ants"] = spawn_ants(state["colony"])
        state["generation"] = 1
        state["best_distance_history"] = []
        state["bfs_result"] = None
        state["astar_result"] = None
        state["simulation_complete"] = False
        state["generation_duration"] = estimate_generation_duration(
            state["active_ants"]
        )
        state["generation_elapsed"] = 0.0
        state["simulated_elapsed"] = 0.0
        state["run_started_at"] = time.perf_counter()
        state["explored_count"] = 0
        state["search_accumulator"] = 0.0
        state["search_animation_complete"] = False
        return state

    state = reset_state()
    selected_algorithm = "ACO"
    paused = False
    running = True
    generation_limit = 100
    speed_multiplier = 1.0
    fast_forward = False
    search_animation_accumulator = 0.0

    def select_search_algorithm(name):
        nonlocal selected_algorithm
        selected_algorithm = name
        state[f"{'bfs' if name == 'BFS' else 'astar'}_result"] = (
            create_algorithm_result(name, state)
        )
        state["explored_count"] = 0
        state["search_accumulator"] = 0.0
        state["search_animation_complete"] = False

    def restart_aco():
        nonlocal state, selected_algorithm, fast_forward
        selected_algorithm = "ACO"
        fast_forward = False
        graph = state["graph"]
        for edge in graph.edges.values():
            edge["pheromone"] = 1.0
        state = reset_state()

    def advance_generation_fast():
        """Finish the current and remaining generations without ant animation."""
        nonlocal state

        # Count the remaining normal-speed animation time for this generation.
        state["simulated_elapsed"] += max(
            0.0,
            state["generation_duration"] - state["generation_elapsed"],
        )
        state["generation_elapsed"] = state["generation_duration"]
        state["active_ants"] = []

        while state["generation"] < generation_limit:
            state["active_ants"] = spawn_ants(state["colony"])
            state["generation"] += 1
            state["best_distance_history"].append(
                state["colony"].best_distance
            )
            duration = estimate_generation_duration(state["active_ants"])
            state["simulated_elapsed"] += duration
            state["generation_duration"] = duration
            state["generation_elapsed"] = duration
            state["active_ants"] = []

        state["simulation_complete"] = True

    while running:
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_b:
                select_search_algorithm("BFS")
            elif event.key == pygame.K_t:
                select_search_algorithm("A*")
            elif event.key == pygame.K_a:
                restart_aco()
            elif event.key == pygame.K_r:
                state = reset_state()
                if selected_algorithm in ("BFS", "A*"):
                    select_search_algorithm(selected_algorithm)
            elif event.key == pygame.K_1:
                generation_limit = 100
                if selected_algorithm == "ACO":
                    state["simulation_complete"] = False
            elif event.key == pygame.K_2:
                generation_limit = 200
                if selected_algorithm == "ACO":
                    state["simulation_complete"] = False
            elif event.key == pygame.K_3:
                generation_limit = 300
                if selected_algorithm == "ACO":
                    state["simulation_complete"] = False
            elif event.key in (
                pygame.K_EQUALS,
                pygame.K_PLUS,
                pygame.K_KP_PLUS,
            ):
                speed_multiplier = min(MAX_SPEED, speed_multiplier + SPEED_STEP)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                speed_multiplier = max(MIN_SPEED, speed_multiplier - SPEED_STEP)
            elif event.key == pygame.K_0:
                speed_multiplier = 1.0
            elif event.key == pygame.K_f:
                fast_forward = not fast_forward
                if fast_forward and selected_algorithm == "ACO":
                    advance_generation_fast()

        if not paused:
            if (
                selected_algorithm == "ACO"
                and not state["simulation_complete"]
                and not fast_forward
            ):
                state["active_ants"] = update_ants(
                    state["active_ants"],
                    delta_time,
                    speed_multiplier,
                )

                # Simulated elapsed is expressed as equivalent time at 1x speed.
                state["generation_elapsed"] = min(
                    state["generation_duration"],
                    state["generation_elapsed"] + delta_time * speed_multiplier,
                )
                state["simulated_elapsed"] += delta_time * speed_multiplier

                if not state["active_ants"]:
                    if state["generation"] >= generation_limit:
                        state["simulation_complete"] = True
                    else:
                        state["active_ants"] = spawn_ants(state["colony"])
                        state["generation"] += 1
                        state["best_distance_history"].append(
                            state["colony"].best_distance
                        )
                        state["generation_duration"] = estimate_generation_duration(
                            state["active_ants"]
                        )
                        state["generation_elapsed"] = 0.0

            elif (
                selected_algorithm in ("BFS", "A*")
                and not state["search_animation_complete"]
            ):
                result_key = "bfs_result" if selected_algorithm == "BFS" else "astar_result"
                result = state.get(result_key)
                if result is not None:
                    state["search_accumulator"] += (
                        delta_time * SEARCH_NODES_PER_SECOND * speed_multiplier
                    )
                    reveal_count = int(state["search_accumulator"])
                    if reveal_count:
                        state["search_accumulator"] -= reveal_count
                        state["explored_count"] = min(
                            len(result.explored_nodes),
                            state["explored_count"] + reveal_count,
                        )
                    if state["explored_count"] >= len(result.explored_nodes):
                        state["search_animation_complete"] = True

        # -------------------------------------------------------------------
        # Draw frame
        # -------------------------------------------------------------------
        screen.fill(BACKGROUND)

        title = title_font.render(f"{selected_algorithm} | GRID PATHFINDING", True, TEXT_COLOR)
        screen.blit(title, (30, TITLE_Y))

        pygame.draw.rect(screen, PANEL_COLOR, grid_panel, border_radius=10)
        pygame.draw.rect(screen, GRID_COLOR, grid_panel, width=1, border_radius=10)

        result = None
        visible_explored = []
        path_to_draw = []

        if selected_algorithm in ("BFS", "A*"):
            key = "bfs_result" if selected_algorithm == "BFS" else "astar_result"
            result = state.get(key)
            if result is not None:
                visible_explored = result.explored_nodes[:state["explored_count"]]
                if state["search_animation_complete"]:
                    path_to_draw = result.path
        else:
            path_to_draw = state["shortest_path"]

        draw_grid(
            screen,
            state["obstacles"],
            path_to_draw,
            state["start"],
            state["destination"],
            explored_nodes=visible_explored,
        )

        if selected_algorithm == "ACO":
            draw_pheromones(screen, state["graph"])
            draw_best_path(screen, state["colony"].best_path)
            draw_ants(screen, state["active_ants"])

        # Metrics panel
        draw_panel(screen, metrics_panel, "RUN METRICS", panel_font)
        if selected_algorithm == "ACO":
            colony = state["colony"]
            best_distance = colony.best_distance
            best_text = (
                f"{best_distance:.0f} steps"
                if math.isfinite(best_distance)
                else "Not found yet"
            )
            optimal_path = state["shortest_path"]
            optimal_text = (
                f"{len(optimal_path) - 1} steps" if optimal_path else "Unavailable"
            )
            if optimal_path and math.isfinite(best_distance):
                optimal_distance = len(optimal_path) - 1
                gap = (
                    (best_distance - optimal_distance) / optimal_distance * 100
                    if optimal_distance else 0.0
                )
                gap_text = f"{gap:.1f}%"
            else:
                gap_text = "Unavailable"

            wall_elapsed = time.perf_counter() - state["run_started_at"]
            metrics = [
                "Algorithm: Ant Colony Optimization (ACO)",
                f"Generation: {state['generation']} / {generation_limit}",
                f"Active ants: {len(state['active_ants'])}    Obstacles: {len(state['obstacles'])}",
                f"Best ACO distance: {best_text}",
                f"BFS optimal distance: {optimal_text}    Optimality gap: {gap_text}",
                f"Simulated elapsed (1x equivalent): {format_duration(state['simulated_elapsed'])}",
                f"Wall-clock elapsed this run: {format_duration(wall_elapsed)}",
                f"Speed: {speed_multiplier:.1f}x    Fast-forward: {'ON' if fast_forward else 'OFF'}",
                f"Run status: {'Complete' if state['simulation_complete'] else 'Running'}",
            ]
        else:
            distance = (
                f"{result.distance:.0f} steps"
                if result is not None and result.found
                else "No path"
            )
            nodes_explored = result.nodes_explored if result is not None else 0
            total_nodes = len(result.explored_nodes) if result is not None else 0
            animation_status = (
                "Exploration complete"
                if state["search_animation_complete"]
                else f"Exploring nodes: {state['explored_count']} / {total_nodes}"
            )
            metrics = [
                f"Algorithm: {'Breadth-First Search (BFS)' if selected_algorithm == 'BFS' else 'A* Search'}",
                f"Path distance: {distance}",
                f"Nodes explored: {nodes_explored}",
                f"Path found: {'Yes' if result is not None and result.found else 'No'}",
                animation_status,
                f"Obstacles: {len(state['obstacles'])}",
            ]

        draw_lines(screen, body_font, metrics, PANEL_X + 14, metrics_panel.y + 45, 27)

        # Controls panel
        draw_panel(screen, controls_panel, "CONTROLS", panel_font)
        controls = [
            "B: BFS    T: A*    A: restart ACO",
            "R: new grid    SPACE: pause / resume",
            "+ / -: speed    0: reset speed",
            "F: fast-forward to generation limit",
            "1: 100 gens    2: 200 gens    3: 300 gens",
            "ESC: quit",
        ]
        draw_lines(screen, body_font, controls, PANEL_X + 14, controls_panel.y + 42, 19)

        # Convergence graph panel
        draw_panel(screen, graph_panel, "ACO CONVERGENCE", panel_font)
        if selected_algorithm == "ACO":
            draw_convergence_graph(
                screen,
                state["best_distance_history"],
                small_font,
            )
        else:
            screen.blit(
                small_font.render(
                    "Switch to ACO to view best-distance convergence.",
                    True,
                    MUTED_TEXT,
                ),
                (GRAPH_X, GRAPH_Y + 16),
            )

        # Legend panel
        draw_panel(screen, legend_panel, "GRID LEGEND", panel_font)
        draw_legend(screen, small_font, PANEL_X + 14, legend_panel.y + 42)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
