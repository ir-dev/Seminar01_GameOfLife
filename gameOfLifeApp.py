from enum import Enum
from os import urandom
import math
import pygame

from cellMapPreset import CellMapPreset


WINDOW_INITIAL_SIZE = (1280, 720)
FPS = 60.0
CELL_SIZE = 10
CELL_MAP_PRESET_DEFAULT = CellMapPreset.EMPTY


class GameOfLifeApp:
    class Color(Enum):
        BABY_YELLOW = (0xFF, 0xFC, 0xC9)
        DARK_GRAY = (0x20, 0x20, 0x20)
        DEEP_DARK_BLUE = (0x0B, 0x0D, 0x2A)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("John Conway's Game of Life")

        self.window_surface = pygame.display.set_mode(WINDOW_INITIAL_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self, initial_configuration=None):
        # Use initial_configuration if provided, otherwise use self.initial_configuration if set, otherwise use default
        if initial_configuration is None:
            if not hasattr(self, 'initial_configuration') or self.initial_configuration is None:
                initial_configuration = self.get_cell_map(CELL_MAP_PRESET_DEFAULT)
            else:
                initial_configuration = self.initial_configuration

        self.initial_configuration = initial_configuration
        self.cell_map = initial_configuration
        # will be drawn in game loop
        self.cell_map_surface = None

    def get_cell_map(self, cell_map_preset: CellMapPreset = CellMapPreset.EMPTY):
        window_size = self.window_surface.get_size()
        window_width, window_height = window_size
        cells_num_x = window_width // CELL_SIZE
        cells_num_y = window_height // CELL_SIZE
        range_x = range(cells_num_x)
        range_y = range(cells_num_y)
        match cell_map_preset:
            case CellMapPreset.EMPTY:
                cell_map = [[0 for x in range_x] for y in range_y]
            case CellMapPreset.RANDOM:
                required_random_bytes = math.ceil((cells_num_x * cells_num_y) / 8)
                random_bits = [(b >> i) & 1 for b in urandom(required_random_bytes) for i in range(8)]
                cell_map = [[random_bits[y * cells_num_x + x] for x in range_x] for y in range_y]
        return cell_map
        return len(self.cell_map)

    def detect_grid_scaling(self):
        window_size = self.window_surface.get_size()
        window_width, window_height = window_size
        cells_num_x = window_width // CELL_SIZE
        cells_num_y = window_height // CELL_SIZE
        actual_cells_num_x = len(self.cell_map[0])
        actual_cells_num_y = len(self.cell_map)
        if cells_num_x != actual_cells_num_x or cells_num_y != actual_cells_num_y:
            # TODO: reuse existing cell_map and only add/remove rows/columns
            self.reset(self.get_cell_map(CELL_MAP_PRESET_DEFAULT))

    def process_events(self):
        def is_cell_collision(point):
            cell_map_rect = pygame.Rect(0, 0, len(self.cell_map[0]) * CELL_SIZE, len(self.cell_map) * CELL_SIZE)
            return cell_map_rect.collidepoint(point)

        def is_cell_modified(point):
            return any([modified_cell_rect.collidepoint(point) for modified_cell_rect in self.modified_cell_rects])

        def toggle_cell_at(mx, my):
            if not is_cell_collision((mx, my)):
                return

            # edge case handling (when mouse is at the right or bottom edge of the cell map)
            cell_map_width = len(self.cell_map[0]) * CELL_SIZE
            cell_map_height = len(self.cell_map) * CELL_SIZE
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
                            self.reset(self.get_cell_map(CellMapPreset.EMPTY))
                        # reset
                        case pygame.K_r:
                            self.reset()
                        # new
                        case pygame.K_n:
                            self.reset(self.get_cell_map(CellMapPreset.RANDOM))
                        # save
                        case pygame.K_s:
                            # TODO
                            pass
                        # load
                        case pygame.K_l:
                            # TODO
                            pass
                        # decrease step speed
                        case pygame.K_LEFT:
                            # TODO
                            pass
                        # increase step speed
                        case pygame.K_RIGHT:
                            # TODO
                            pass
                        # increase grid size
                        case pygame.K_UP:
                            # TODO
                            pass
                        # decrease grid size
                        case pygame.K_DOWN:
                            # TODO
                            pass
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

    @ staticmethod
    def simulate_map(cell_map):
        cells_num_x = len(cell_map[0])
        cells_num_y = len(cell_map)
        # TODO: use 2 line buffers instead of copying the whole map; modify the cell_map in-place without returning a new map
        new_cell_map = [[0 for x in range(cells_num_x)] for y in range(cells_num_y)]

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
                    mid_neighbours[x-1] if x >= 0 else True,
                    mid_neighbours[x+1] if x < cells_num_x - 1 else 0,
                    lower_neighbours[x-1] if x >= 0 else True,
                    lower_neighbours[x],
                    lower_neighbours[x+1] if x < cells_num_x - 1 else 0
                ]

                own_active = own == 1
                neighbours_sum = sum(neighbours)
                # Reproduction/birth of a cell: If a dead cell has exactly three living neighbors, the cell is alive in the next generation step
                if not own_active and neighbours_sum == 3:
                    new_cell_map[y][x] = 1
                # Death by overpopulation: If a living cell has more than three neighbors, the cell dies
                elif own_active and neighbours_sum > 3:
                    new_cell_map[y][x] = 0
                # Dead due to missing neighbors: If a living cell has less than two neighbors, the cell dies
                elif own_active and neighbours_sum < 2:
                    new_cell_map[y][x] = 0
                # Survival: If a living cell has two or three neighbors, the cell remains alive
                elif own_active and neighbours_sum in [2, 3]:
                    new_cell_map[y][x] = 1
        return new_cell_map

    @ staticmethod
    def get_cell_map_surface(cell_map, cell_size):
        cells_num_x = len(cell_map[0])
        cells_num_y = len(cell_map)
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

    def run(self):
        self.running = True
        self.paused = True
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.process_events()
            self.detect_grid_scaling()

            # game logic
            window_size = self.window_surface.get_size()
            if not self.paused:
                self.cell_map = self.simulate_map(self.cell_map)

            # draw graphics
            background_surface = pygame.Surface(window_size)
            background_surface.fill(self.Color.DARK_GRAY.value)
            cell_map_surface = self.get_cell_map_surface(self.cell_map, CELL_SIZE)

            self.window_surface.blit(background_surface, (0, 0))
            self.window_surface.blit(cell_map_surface, (0, 0))

            pygame.display.flip()
