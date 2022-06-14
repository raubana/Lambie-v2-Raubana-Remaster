import multiprocessing
import math

import common

VERBOSE_LEVEL = 5

KERNEL_SIZE = 3
SIGMA = ((KERNEL_SIZE / 2.0) - 1.0)

DISPLACEMENT_OFFSETS_AND_WEIGHTS = []
for y in range(-KERNEL_SIZE // 2, (KERNEL_SIZE // 2) + 1):
    for x in range(-KERNEL_SIZE // 2, (KERNEL_SIZE // 2) + 1):
        if not (x == 0 and y == 0):
            radius = math.sqrt((x ** 2) + (y ** 2))
            DISPLACEMENT_OFFSETS_AND_WEIGHTS.append(((x, y), common.new_math.gaussian_function(radius, 1.0, 0.0, SIGMA)))

PRINT_LOCK = multiprocessing.Lock()