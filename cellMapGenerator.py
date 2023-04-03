from enum import Enum
import math
from os import urandom


class CellMapPreset(Enum):
    EMPTY = 0
    RANDOM = 1
    STILLLIFE_BLOCK = 2
    OSCILLATOR_BLINKER = 3
    SPACESHIP_GLIDER = 4
    GUN_GOSPER_GLIDER_GUN = 5
    METHUSELAH_DIEHARD = 6


class CellMapGenerator:
    @staticmethod
    def get_cell_map(map_size, cell_map_preset: CellMapPreset = CellMapPreset.EMPTY):
        cells_num_x, cells_num_y = map_size
        range_x = range(cells_num_x)
        range_y = range(cells_num_y)
        # modes
        match cell_map_preset:
            case CellMapPreset.EMPTY:
                return [[0 for x in range_x] for y in range_y]
            case CellMapPreset.RANDOM:
                required_random_bytes = math.ceil((cells_num_x * cells_num_y) / 8)
                random_bits = [(b >> i) & 1 for b in urandom(required_random_bytes) for i in range(8)]
                return [[random_bits[y * cells_num_x + x] for x in range_x] for y in range_y]
        # patterns
        match cell_map_preset:
            case CellMapPreset.STILLLIFE_BLOCK:
                cell_pattern = [[1, 1], [1, 1]]
            case CellMapPreset.OSCILLATOR_BLINKER:
                cell_pattern = [[1, 1, 1]]
            case CellMapPreset.SPACESHIP_GLIDER:
                cell_pattern = [[0, 1, 0], [0, 0, 1], [1, 1, 1]]
            case CellMapPreset.GUN_GOSPER_GLIDER_GUN:
                cell_pattern = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
                                    0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, ],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0,
                                    0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, ],
                                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                                    0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0,
                                    0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                                    0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]]
            case CellMapPreset.METHUSELAH_DIEHARD:
                cell_pattern = [[0, 0, 0, 0, 0, 0, 1, 0], [1, 1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1, 1, 1]]
        return CellMapGenerator.get_cell_map_with_pattern(map_size, cell_pattern)

    @staticmethod
    def get_cell_map_with_pattern(map_size, cell_pattern):
        cells_num_x, cells_num_y = map_size
        cell_pattern_num_x = len(cell_pattern[0])
        cell_pattern_num_y = len(cell_pattern)

        if cell_pattern_num_x > cells_num_x or cell_pattern_num_y > cells_num_y:
            raise ValueError("cell pattern is too big")

        cell_map_with_pattern = CellMapGenerator.get_cell_map(map_size, CellMapPreset.EMPTY)
        for y in range(cell_pattern_num_y):
            for x in range(cell_pattern_num_x):
                cell_map_with_pattern[y][x] = cell_pattern[y][x]
        return cell_map_with_pattern
