import pygame  # type: ignore
import asyncio
import json
import os
from queue import PriorityQueue

pygame.display.init()
pygame.font.init()

WIDTH = 800
SIDEBAR_WIDTH = 300
ROWS = 50

WIN = None

FLOORPLANS_FILE = "saved_floorplans.json"

saved_floorplans = []

selected_floorplan = None

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:

    def __init__(self, row, col, width, total_rows):

        self.row = row
        self.col = col

        self.x = row * width
        self.y = col * width

        self.color = WHITE

        self.neighbors = []

        self.width = width
        self.total_rows = total_rows

    def get_pos(self):

        return self.row, self.col

    def is_barrier(self):

        return self.color == BLACK

    def is_start(self):

        return self.color == ORANGE

    def is_end(self):

        return self.color == TURQUOISE

    def reset(self):

        self.color = WHITE

    def make_start(self):

        self.color = ORANGE

    def make_closed(self):

        self.color = RED

    def make_open(self):

        self.color = GREEN

    def make_barrier(self):

        self.color = BLACK

    def make_end(self):

        self.color = TURQUOISE

    def make_path(self):

        self.color = PURPLE

    def draw(self, win):

        pygame.draw.rect(

            win,

            self.color,

            (
                self.x,
                self.y,
                self.width,
                self.width
            )
        )

    def update_neighbors(self, grid):

        self.neighbors = []

        if (
            self.row < self.total_rows - 1 and
            not grid[self.row + 1][self.col].is_barrier()
        ):
            self.neighbors.append(
                grid[self.row + 1][self.col]
            )

        if (
            self.row > 0 and
            not grid[self.row - 1][self.col].is_barrier()
        ):
            self.neighbors.append(
                grid[self.row - 1][self.col]
            )

        if (
            self.col < self.total_rows - 1 and
            not grid[self.row][self.col + 1].is_barrier()
        ):
            self.neighbors.append(
                grid[self.row][self.col + 1]
            )

        if (
            self.col > 0 and
            not grid[self.row][self.col - 1].is_barrier()
        ):
            self.neighbors.append(
                grid[self.row][self.col - 1]
            )

    def __lt__(self, other):

        return False


def load_floorplans():

    global saved_floorplans

    if os.path.exists(FLOORPLANS_FILE):

        with open(FLOORPLANS_FILE, "r") as file:

            saved_floorplans = json.load(file)

    else:

        saved_floorplans = []


def save_floorplans():

    with open(FLOORPLANS_FILE, "w") as file:

        json.dump(
            saved_floorplans,
            file,
            indent=4
        )


def save_current_floorplan(grid):

    global selected_floorplan

    if selected_floorplan is None:
        return

    walls = []
    exits = []

    for row in grid:

        for spot in row:

            if spot.is_barrier():

                walls.append([
                    spot.row,
                    spot.col
                ])

            if spot.is_end():

                exits.append([
                    spot.row,
                    spot.col
                ])

    floorplan_data = {

        "name": selected_floorplan,

        "walls": walls,

        "exits": exits
    }

    replaced = False

    for i, fp in enumerate(saved_floorplans):

        if fp["name"] == selected_floorplan:

            saved_floorplans[i] = floorplan_data

            replaced = True

    if not replaced:

        saved_floorplans.append(
            floorplan_data
        )

    save_floorplans()


def delete_floorplan(name):

    global saved_floorplans

    saved_floorplans = [

        fp for fp in saved_floorplans

        if fp["name"] != name
    ]

    save_floorplans()


def load_floorplan_into_grid(grid, floorplan):

    for row in grid:

        for spot in row:

            spot.reset()

    for wall in floorplan["walls"]:

        grid[
            wall[0]
        ][
            wall[1]
        ].make_barrier()

    for ex in floorplan["exits"]:

        grid[
            ex[0]
        ][
            ex[1]
        ].make_end()


def draw_sidebar(win, mode):

    pygame.draw.rect(

        win,

        (40, 40, 40),

        (
            WIDTH,
            0,
            SIDEBAR_WIDTH,
            WIDTH
        )
    )

    font = pygame.font.SysFont(
        "Arial",
        24
    )

    title = font.render(

        "Saved Floorplans",

        True,

        WHITE
    )

    win.blit(title, (WIDTH + 20, 20))

    button_font = pygame.font.SysFont(
        "Arial",
        18
    )

    add_rect = pygame.Rect(
        WIDTH + 20,
        70,
        250,
        40
    )

    pygame.draw.rect(
        win,
        BLUE,
        add_rect
    )

    add_text = button_font.render(

        "Add Floorplan",

        True,

        WHITE
    )

    win.blit(add_text, (WIDTH + 40, 80))

    y = 140

    for fp in saved_floorplans:

        floor_rect = pygame.Rect(
            WIDTH + 20,
            y,
            170,
            40
        )

        delete_rect = pygame.Rect(
            WIDTH + 200,
            y,
            70,
            40
        )

        pygame.draw.rect(
            win,
            GREY,
            floor_rect
        )

        pygame.draw.rect(
            win,
            RED,
            delete_rect
        )

        text = button_font.render(
            fp["name"],
            True,
            WHITE
        )

        delete_text = button_font.render(
            "DEL",
            True,
            WHITE
        )

        win.blit(
            text,
            (WIDTH + 30, y + 10)
        )

        win.blit(
            delete_text,
            (WIDTH + 215, y + 10)
        )

        y += 60

    mode_font = pygame.font.SysFont(
        "Arial",
        22
    )

    mode_text = mode_font.render(

        f"Mode: {mode.upper()}",

        True,

        WHITE
    )

    win.blit(
        mode_text,
        (WIDTH + 20, 700)
    )

    instructions = [

        "1 = Wall Mode",

        "2 = Exit Mode",

        "3 = Start Mode",

        "LEFT CLICK = Place",

        "RIGHT CLICK = Erase",

        "SPACE = Run A*",

        "S = Save"
    ]

    small_font = pygame.font.SysFont(
        "Arial",
        16
    )

    y = 740

    for line in instructions:

        txt = small_font.render(
            line,
            True,
            WHITE
        )

        win.blit(
            txt,
            (WIDTH + 20, y)
        )

        y += 22


def h(p1, p2):

    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


async def reconstruct_path(
    came_from,
    current,
    draw_fn
):

    while current in came_from:

        current = came_from[current]

        current.make_path()

        await draw_fn()


async def algorithm(
    draw_fn,
    grid,
    start,
    end
):

    count = 0

    open_set = PriorityQueue()

    open_set.put((0, count, start))

    came_from = {}

    g_score = {
        spot: float("inf")
        for row in grid
        for spot in row
    }

    g_score[start] = 0

    f_score = {
        spot: float("inf")
        for row in grid
        for spot in row
    }

    f_score[start] = h(
        start.get_pos(),
        end.get_pos()
    )

    open_set_hash = {start}

    while not open_set.empty():

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()

                return False

        current = open_set.get()[2]

        open_set_hash.remove(current)

        if current == end:

            await reconstruct_path(
                came_from,
                end,
                draw_fn
            )

            end.make_end()

            return True

        for neighbor in current.neighbors:

            temp_g_score = (
                g_score[current] + 1
            )

            if temp_g_score < g_score[neighbor]:

                came_from[neighbor] = current

                g_score[neighbor] = temp_g_score

                f_score[neighbor] = (

                    temp_g_score +

                    h(
                        neighbor.get_pos(),
                        end.get_pos()
                    )
                )

                if neighbor not in open_set_hash:

                    count += 1

                    open_set.put(

                        (
                            f_score[neighbor],
                            count,
                            neighbor
                        )
                    )

                    open_set_hash.add(neighbor)

                    neighbor.make_open()

        await draw_fn()

        if current != start:

            current.make_closed()

        await asyncio.sleep(0)

    return False


def make_grid(rows, width):

    grid = []

    gap = width // rows

    for i in range(rows):

        grid.append([])

        for j in range(rows):

            spot = Spot(
                i,
                j,
                gap,
                rows
            )

            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):

    gap = width // rows

    for i in range(rows):

        pygame.draw.line(
            win,
            GREY,
            (0, i * gap),
            (width, i * gap)
        )

        for j in range(rows):

            pygame.draw.line(
                win,
                GREY,
                (j * gap, 0),
                (j * gap, width)
            )


async def draw(win, grid, rows, width, mode):

    win.fill(WHITE)

    for row in grid:

        for spot in row:

            spot.draw(win)

    draw_grid(win, rows, width)

    draw_sidebar(win, mode)

    pygame.display.update()

    await asyncio.sleep(0)


def get_clicked_pos(pos, rows, width):

    gap = width // rows

    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


async def main():

    global WIN
    global selected_floorplan

    load_floorplans()

    WIN = pygame.display.set_mode(
        (
            WIDTH + SIDEBAR_WIDTH,
            WIDTH
        )
    )

    pygame.display.set_caption(
        "SafeRoute Floorplan Editor"
    )

    grid = make_grid(ROWS, WIDTH)

    start = None

    ends = []

    mode = "wall"

    run = True

    while run:

        await draw(
            WIN,
            grid,
            ROWS,
            WIDTH,
            mode
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = pygame.mouse.get_pos()

                if mouse_x > WIDTH:

                    add_button = pygame.Rect(
                        WIDTH + 20,
                        70,
                        250,
                        40
                    )

                    if add_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        selected_floorplan = input(
                            "Enter floorplan name: "
                        )

                    y = 140

                    for fp in saved_floorplans:

                        floor_rect = pygame.Rect(
                            WIDTH + 20,
                            y,
                            170,
                            40
                        )

                        delete_rect = pygame.Rect(
                            WIDTH + 200,
                            y,
                            70,
                            40
                        )

                        if floor_rect.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            selected_floorplan = fp["name"]

                            load_floorplan_into_grid(
                                grid,
                                fp
                            )

                            start = None
                            ends = []

                        if delete_rect.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            delete_floorplan(
                                fp["name"]
                            )

                        y += 60

            if pygame.mouse.get_pressed()[0]:

                raw_pos = pygame.mouse.get_pos()

                if raw_pos[0] < WIDTH:

                    actual_y = min(
                        int(raw_pos[0]),
                        WIDTH - 1
                    )

                    actual_x = min(
                        int(raw_pos[1]),
                        WIDTH - 1
                    )

                    row, col = get_clicked_pos(
                        (
                            actual_y,
                            actual_x
                        ),
                        ROWS,
                        WIDTH
                    )

                    if (
                        0 <= row < ROWS and
                        0 <= col < ROWS
                    ):

                        spot = grid[row][col]

                        if mode == "start":

                            if start:

                                start.reset()

                            start = spot

                            start.make_start()

                        elif mode == "exit":

                            if (
                                spot != start and
                                spot not in ends
                            ):

                                ends.append(spot)

                                spot.make_end()

                        elif mode == "wall":

                            if (
                                spot != start and
                                spot not in ends
                            ):

                                spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:

                raw_pos = pygame.mouse.get_pos()

                if raw_pos[0] < WIDTH:

                    actual_y = min(
                        int(raw_pos[0]),
                        WIDTH - 1
                    )

                    actual_x = min(
                        int(raw_pos[1]),
                        WIDTH - 1
                    )

                    row, col = get_clicked_pos(
                        (
                            actual_y,
                            actual_x
                        ),
                        ROWS,
                        WIDTH
                    )

                    if (
                        0 <= row < ROWS and
                        0 <= col < ROWS
                    ):

                        spot = grid[row][col]

                        spot.reset()

                        if spot == start:

                            start = None

                        elif spot in ends:

                            ends.remove(spot)

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:

                    mode = "wall"

                if event.key == pygame.K_2:

                    mode = "exit"

                if event.key == pygame.K_3:

                    mode = "start"

                if (
                    event.key == pygame.K_SPACE and
                    start and
                    len(ends) > 0
                ):

                    shortest_exit = None

                    shortest_length = float("inf")

                    for end in ends:

                        for row in grid:

                            for spot in row:

                                if (
                                    not spot.is_barrier() and
                                    not spot.is_start() and
                                    not spot.is_end()
                                ):

                                    spot.reset()

                        for row in grid:

                            for spot in row:

                                spot.update_neighbors(
                                    grid
                                )

                        found = await algorithm(

                            lambda: draw(
                                WIN,
                                grid,
                                ROWS,
                                WIDTH,
                                mode
                            ),

                            grid,
                            start,
                            end
                        )

                        if found:

                            path_length = 0

                            for row in grid:

                                for spot in row:

                                    if spot.color == PURPLE:

                                        path_length += 1

                            if path_length < shortest_length:

                                shortest_length = path_length

                                shortest_exit = end

                    if shortest_exit:

                        for row in grid:

                            for spot in row:

                                if (
                                    not spot.is_barrier() and
                                    not spot.is_start() and
                                    not spot.is_end()
                                ):

                                    spot.reset()

                        for row in grid:

                            for spot in row:

                                spot.update_neighbors(
                                    grid
                                )

                        await algorithm(

                            lambda: draw(
                                WIN,
                                grid,
                                ROWS,
                                WIDTH,
                                mode
                            ),

                            grid,
                            start,
                            shortest_exit
                        )

                if event.key == pygame.K_s:

                    save_current_floorplan(
                        grid
                    )

                if event.key == pygame.K_c:

                    start = None

                    ends = []

                    grid = make_grid(
                        ROWS,
                        WIDTH
                    )

        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())