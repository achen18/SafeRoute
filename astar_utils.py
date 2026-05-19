import heapq
from typing import List, Tuple, Set
from matplotlib.path import Path

# Grid configuration matching the system requirements
GRID_ROWS = 50
GRID_COLS = 50
GRID_SIZE = 16

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """
    Calculates the Manhattan distance between two cells.

    Args:
        a (Tuple[int, int]): starting coordinate pair, (col, row)
        b (Tuple[int, int]): destination coordinate grid pair, (col, row)

    Returns:
        int: absolute grid distance between a and b
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def polygon_to_cells(points: List[List[float]]) -> Set[Tuple[int, int]]:
    """
    Converts a polygon bounding box (from UI zones) into 
    grid cell coordinates that match the 50x50 matrix layout.

    Arguments:
        points (List[List[float]]): floating point coordinate pairs defining a boundary

    Returns:
        Set[Tuple[int, int]]: set of integer cell coordinates (col, row) enclosed by the boundary
    
    """
    poly = Path(points)
    cells = set()

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            px = col * GRID_SIZE + GRID_SIZE / 2
            py = row * GRID_SIZE + GRID_SIZE / 2

            if poly.contains_point((px, py)):
                cells.add((col, row))

    return cells


def astar(
    start: Tuple[int, int], 
    goal: Tuple[int, int], 
    walls: Set[Tuple[int, int]], 
    danger: Set[Tuple[int, int]], 
    safe: Set[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    Executes the pathfinding calculation across the matrix array.
    Applies lower costs to designated safe paths and blocks danger areas.

    Arguments:
        start (Tuple[int, int]): given coordinate pair
        goal (Tuple[int, int]): target coordinate pair
        walls (Set[Tuple[int, int]]): Coordinates of physical obstructions which block movement
        danger (Set[Tuple[int, int]]): hazard threat area coordinates to stay away from
        safe (Set[Tuple[int, int]]): secured area coordinates offering favorable evacuation

    Returns:
        List[Tuple[int, int]]: ordered sequential array of nodes from start to target. Returns empty if unroutable
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        neighbors = [
            (current[0] + 1, current[1]),
            (current[0] - 1, current[1]),
            (current[0], current[1] + 1),
            (current[0], current[1] - 1)
        ]

        for n in neighbors:
            # Boundary control checks
            if n[0] < 0 or n[1] < 0 or n[0] >= GRID_COLS or n[1] >= GRID_ROWS:
                continue

            if n in walls:
                continue

            if n in danger:
                continue

            # Base cost for passing through a cell
            move_cost = 1

            # Reduce path cost weight if the cell sits inside a safe zone
            if n in safe:
                move_cost -= 0.2

            tentative = g_score[current] + move_cost

            if n not in g_score or tentative < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative
                f = tentative + heuristic(n, goal)
                heapq.heappush(open_set, (f, n))

    return []