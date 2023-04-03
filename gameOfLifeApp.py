from enum import Enum
import random
import pygame

from cellMapGenerator import CellMapGenerator, CellMapPreset


WINDOW_INITIAL_SIZE = (1280, 720)
SIMULATION_INITIAL_SPEED = 30
SIMULATION_STOP_SIGNAL_CHECK_STEP = 1000
SIMULATION_MIN_SPEED = 1
SIMULATION_MAX_SPEED = 1000
FPS = 60.0
CELL_SIZE = 10
CELL_MAP_PRESET_DEFAULT = CellMapPreset.EMPTY


class GameOfLifeApp:
    class Color(Enum):
        BABY_YELLOW = (0xFF, 0xFC, 0xC9)
        DARK_GRAY = (0x20, 0x20, 0x20)
        DEEP_DARK_BLUE = (0x0B, 0x0D, 0x2A)
        WHITE = (0xFF, 0xFF, 0xFF)

    class SimulationState(Enum):
        CHANGING = 0
        EMPTY = 1
        STABLE = 2

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("John Conway's Game of Life")

        self.font = pygame.font.SysFont('monospace', 16)
        self.window_surface = pygame.display.set_mode(WINDOW_INITIAL_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.simulation_speed = SIMULATION_INITIAL_SPEED
        self.reset()

    def get_available_cell_map_cell_nums(self):
        window_size = self.window_surface.get_size()
        window_width, window_height = window_size
        cells_num_x = window_width // CELL_SIZE
        cells_num_y = window_height // CELL_SIZE
        return cells_num_x, cells_num_y

    @staticmethod
    def get_cell_map_cell_nums_static(cell_map):
        return len(cell_map[0]), len(cell_map)

    def get_cell_map_cell_nums(self):
        return len(self.cell_map[0]), len(self.cell_map)

    def get_cell_map_size(self):
        return len(self.cell_map[0]) * CELL_SIZE, len(self.cell_map) * CELL_SIZE

    def reset(self, initial_configuration=None):
        # Use initial_configuration if provided, otherwise use self.initial_configuration if set, otherwise use default
        if initial_configuration is None:
            if not hasattr(self, 'initial_configuration') or self.initial_configuration is None:
                initial_configuration = CellMapGenerator.get_cell_map(
                    self.get_available_cell_map_cell_nums(), CELL_MAP_PRESET_DEFAULT)
            else:
                initial_configuration = self.initial_configuration

        self.initial_configuration = initial_configuration
        self.cell_map = initial_configuration
        # will be drawn in game loop
        self.cell_map_surface = None
        self.simulation_step = 0

    def process_events(self):
        def is_cell_collision(point):
            cell_map_width, cell_map_height = self.get_cell_map_size()
            cell_map_rect = pygame.Rect(0, 0, cell_map_width, cell_map_height)
            return cell_map_rect.collidepoint(point)

        def is_cell_modified(point):
            return any([modified_cell_rect.collidepoint(point) for modified_cell_rect in self.modified_cell_rects])

        def toggle_cell_at(mx, my):
            if not is_cell_collision((mx, my)):
                return

            # edge case handling (when mouse is at the right or bottom edge of the cell map)
            cell_map_width, cell_map_height = self.get_cell_map_size()
            if mx == cell_map_width:
                x = mx // CELL_SIZE - 1
            else:
                x = mx // CELL_SIZE
            if my == cell_map_height:
                y = my // CELL_SIZE - 1
            else:
                y = my // CELL_SIZE

            self.cell_map[y][x] = 1 - self.cell_map[y][x]
            cell_rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            self.modified_cell_rects.append(cell_rect)

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    match event.key:
                        # exit
                        case pygame.K_ESCAPE:
                            self.running = False
                        # start (or stop)
                        case pygame.K_SPACE:
                            self.paused = not self.paused
                        # clear
                        case pygame.K_c:
                            self.paused = True
                            cell_map = CellMapGenerator.get_cell_map(
                                self.get_available_cell_map_cell_nums(), CellMapPreset.EMPTY)
                            self.reset(cell_map)
                        # reset
                        case pygame.K_r:
                            self.reset()
                        # new
                        case pygame.K_n:
                            cell_map = CellMapGenerator.get_cell_map(
                                self.get_available_cell_map_cell_nums(), CellMapPreset.RANDOM)
                            self.reset(cell_map)
                        # new (with pattern)
                        case pygame.K_p:
                            cell_map_pattern = CellMapPreset(random.randint(2, len(CellMapPreset) - 1))
                            cell_map = CellMapGenerator.get_cell_map(
                                self.get_available_cell_map_cell_nums(), cell_map_pattern)
                            self.reset(cell_map)
                        # save
                        case pygame.K_s:
                            # TODO: save game state and use appropriate data structure
                            pass
                        # load
                        case pygame.K_l:
                            # TODO: load game state
                            pass
                        # decrease step speed (1 means 1 step per 1s)
                        case pygame.K_LEFT:
                            self.simulation_speed = max(SIMULATION_MIN_SPEED, self.simulation_speed - 1)
                        # increase step speed (1 means 1 step per 1s)
                        case pygame.K_RIGHT:
                            self.simulation_speed = min(SIMULATION_MAX_SPEED, self.simulation_speed + 1)
                case pygame.MOUSEBUTTONDOWN:
                    self.dragging = True
                    self.modified_cell_rects = []
                    if event.button == 1 and is_cell_collision(event.pos):
                        self.paused = True
                        mx, my = event.pos
                        toggle_cell_at(mx, my)
                case pygame.MOUSEBUTTONUP:
                    self.dragging = False
                case pygame.MOUSEMOTION:
                    if hasattr(self, 'dragging') and self.dragging:
                        # check if cell was already modified by ongoing drag
                        if not is_cell_modified(event.pos):
                            mx, my = event.pos
                            toggle_cell_at(mx, my)

    def apply_grid_scaling(self):
        available_cells_num_x, available_cells_num_y = self.get_available_cell_map_cell_nums()
        cells_num_x, cells_num_y = self.get_cell_map_cell_nums()
        if available_cells_num_x != cells_num_x or available_cells_num_y != cells_num_y:
            # scale the grid depending on the delta of cell nums (delta < 0: remove rows/columns, delta > 0: add rows/columns)
            cells_delta_x = available_cells_num_x - cells_num_x
            cells_delta_y = available_cells_num_y - cells_num_y
            if cells_delta_x < 0:
                for row in self.cell_map:
                    for _ in range(cells_delta_x * -1):
                        row.pop()
            elif cells_delta_x > 0:
                for row in self.cell_map:
                    for _ in range(cells_delta_x):
                        row.append(0)
            if cells_delta_y < 0:
                for _ in range(cells_delta_y * -1):
                    self.cell_map.pop()
            elif cells_delta_y > 0:
                for _ in range(cells_delta_y):
                    self.cell_map.append([0 for _ in range(available_cells_num_x)])
            self.reset(self.cell_map)

    @ staticmethod
    def simulate_map(cell_map):
        cells_num_x, cells_num_y = GameOfLifeApp.get_cell_map_cell_nums_static(cell_map)

        last_row = [0] * cells_num_x
        curr_row = [0] * cells_num_x

        for y in range(cells_num_y):
            for x in range(cells_num_x):
                own = cell_map[y][x]
                upper_neighbours = cell_map[y-1] if y > 0 else [0] * cells_num_x
                mid_neighbours = cell_map[y]
                lower_neighbours = cell_map[y+1] if y < cells_num_y - 1 else [0] * cells_num_x
                neighbours = [
                    upper_neighbours[x-1] if x > 0 else 0,
                    upper_neighbours[x],
                    upper_neighbours[x+1] if x < cells_num_x - 1 else 0,
                    mid_neighbours[x-1] if x > 0 else 0,
                    mid_neighbours[x+1] if x < cells_num_x - 1 else 0,
                    lower_neighbours[x-1] if x > 0 else 0,
                    lower_neighbours[x],
                    lower_neighbours[x+1] if x < cells_num_x - 1 else 0
                ]

                own_active = own == 1
                neighbours_sum = sum(neighbours)
                # Reproduction/birth of a cell: If a dead cell has exactly three living neighbors, the cell is alive in the next generation step
                if not own_active and neighbours_sum == 3:
                    curr_row[x] = 1
                # Death by overpopulation: If a living cell has more than three neighbors, the cell dies
                elif own_active and neighbours_sum > 3:
                    curr_row[x] = 0
                # Dead due to missing neighbors: If a living cell has less than two neighbors, the cell dies
                elif own_active and neighbours_sum < 2:
                    curr_row[x] = 0
                # Survival: If a living cell has two or three neighbors, the cell remains alive
                elif own_active and neighbours_sum in [2, 3]:
                    curr_row[x] = 1

            if y > 0:
                cell_map[y-1] = last_row.copy()
            if y == cells_num_y - 1:
                cell_map[y] = curr_row.copy()
            last_row, curr_row = curr_row, [0] * cells_num_x

    @ staticmethod
    def get_cell_map_surface(cell_map, cell_size):
        cells_num_x, cells_num_y = GameOfLifeApp.get_cell_map_cell_nums_static(cell_map)
        color_type = GameOfLifeApp.Color
        cell_map_surface = pygame.Surface((cells_num_x * cell_size, cells_num_y * cell_size))
        cell_dead_surface = pygame.Surface((cell_size, cell_size))
        cell_dead_surface.fill(color_type.DEEP_DARK_BLUE.value)
        cell_active_surface = pygame.Surface((cell_size, cell_size))
        cell_active_surface.fill(color_type.BABY_YELLOW.value)
        [pygame.draw.rect(surface, color_type.DARK_GRAY.value, (0, 0, cell_size, 1))
         for surface in [cell_dead_surface, cell_active_surface]]
        [pygame.draw.rect(surface, color_type.DARK_GRAY.value, (cell_size-1, 0, cell_size, cell_size))
         for surface in [cell_dead_surface, cell_active_surface]]
        [pygame.draw.rect(surface, color_type.DARK_GRAY.value, (0, cell_size-1, cell_size, cell_size))
         for surface in [cell_dead_surface, cell_active_surface]]
        [pygame.draw.rect(surface, color_type.DARK_GRAY.value, (0, 0, 1, cell_size))
         for surface in [cell_dead_surface, cell_active_surface]]
        for y in range(cells_num_y):
            for x in range(cells_num_x):
                cell_surface = cell_dead_surface if cell_map[y][x] == 0 else cell_active_surface
                cell_map_surface.blit(cell_surface, (x * CELL_SIZE, y * CELL_SIZE))
        return cell_map_surface

    @ staticmethod
    def determine_simulation_state(cell_map):
        if (sum(sum(y) for y in cell_map) == 0):
            return GameOfLifeApp.SimulationState.EMPTY
        cell_map_next = cell_map.copy()
        GameOfLifeApp.simulate_map(cell_map_next)
        # NOTE: the stable check could be more nuanced by checking for stable patterns
        if cell_map == cell_map_next:
            return GameOfLifeApp.SimulationState.STABLE
        else:
            return GameOfLifeApp.SimulationState.CHANGING

    def run(self):
        self.running = True
        self.paused = True
        dt_simulation = 0
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.process_events()
            self.apply_grid_scaling()

            # game logic
            window_size = self.window_surface.get_size()
            window_width, window_height = window_size
            if not self.paused:
                dt_simulation += dt
                if dt_simulation >= 1 / self.simulation_speed:
                    self.simulate_map(self.cell_map)
                    self.simulation_step += 1
                    dt_simulation = 0

                    if self.simulation_step == SIMULATION_STOP_SIGNAL_CHECK_STEP:
                        state_type = self.SimulationState
                        match self.determine_simulation_state(self.cell_map):
                            case state_type.EMPTY | state_type.STABLE:
                                self.paused = True
            else:
                dt_simulation = 0

            # draw graphics
            background_surface = pygame.Surface(window_size)
            background_surface.fill(self.Color.DARK_GRAY.value)
            cell_map_surface = self.get_cell_map_surface(self.cell_map, CELL_SIZE)

            self.window_surface.blit(background_surface, (0, 0))
            self.window_surface.blit(cell_map_surface, (0, 0))

            paused = "PAUSED " if self.paused else ""
            fps = self.clock.get_fps()
            status_text = "{}FPS: {:.0f} Speed: {} Steps: {}".format(
                paused, fps, self.simulation_speed, self.simulation_step)
            status_text_surface = self.font.render(status_text, True, self.Color.WHITE.value)
            self.window_surface.blit(status_text_surface, (0, window_height - status_text_surface.get_height()))

            pygame.display.flip()
        pygame.freetype.quit()
        pygame.quit()
