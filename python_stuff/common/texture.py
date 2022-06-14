import bpy
import mathutils

import sys
import time
import math
import ctypes
import multiprocessing

import numpy

import constants
import common

from multiprocessing_stuff.__auto_fill_margin_collect_data import __auto_fill_margin_collect_data
from multiprocessing_stuff.__auto_fill_margin_apply_dilation import __auto_fill_margin_apply_dilation


def coords_to_index(coords, size, channels):
    return (coords[0] * channels) + (coords[1] * size[0] * channels)


def index_to_coords(index, size, channels):
    i = index // channels
    x = i % size[0]
    y = i // size[0]
    return x, y


def coords_are_in_image(coords, size):
    return coords[0] >= 0 and coords[1] >= 0 and coords[0] < size[0] and coords[1] < size[1]


def make_blank_image(name, size, color_space="sRGB", fill_color=(0.5, 0.5, 0.5, 0.0)):
    if name in bpy.context.blend_data.images:
        bpy.context.blend_data.images.remove(bpy.context.blend_data.images[name])

    bpy.ops.image.new(
        name=name,
        width=size[0],
        height=size[1],
        color=fill_color,
        alpha=True,
        float=True
    )

    img = bpy.context.blend_data.images[name]
    img.colorspace_settings.name = color_space

    img.update()

    return img


def save_image(image, color_mode, color_depth, save_as_render=True, delete_from_memory=True):
    image.file_format = constants.texture.TEXTURE_FILEFORMAT
    image.filepath_raw = common.general.clean_filepath(constants.texture.TEXTURE_BAKED_FOLDER + image.name)

    image.update()

    bpy.context.scene.render.image_settings.file_format = constants.texture.TEXTURE_FILEFORMAT
    bpy.context.scene.render.image_settings.color_depth = color_depth
    bpy.context.scene.render.image_settings.color_mode = color_mode

    if save_as_render:
        image.save_render(common.general.clean_filepath(constants.texture.TEXTURE_BAKED_FOLDER + image.name))
    else:
        image.save()

    if delete_from_memory:
        bpy.context.blend_data.images.remove(image)


def bleed_opaque_into_non_opaque(image):
    old_pixels = list(image.pixels)
    new_pixels = list(image.pixels)

    edge_pixels = range(0, image.size[0] * image.size[1] * image.channels, image.channels)

    last_edge_pixel_count = len(edge_pixels)
    last_delta = 0

    iteration = 0
    while len(edge_pixels) > 0:
        delta = len(edge_pixels) - last_edge_pixel_count
        deltadelta = delta - last_delta

        last_delta = delta

        common.general.safe_print(" ---- edge pixel count:", len(edge_pixels), " (\U00000394", delta,
                                  ", \U00000394\U00000394",
                                  deltadelta, ") iteration:", iteration)

        last_edge_pixel_count = len(edge_pixels)

        displace_data = {}

        # of the pixels in edge_pixels, we collect the opaque ones that have one or more translucent neighbor.
        for i in edge_pixels:
            our_pixel = new_pixels[i:i + image.channels]
            if our_pixel[-1] >= 1.0:
                x, y = index_to_coords(i, image.size, image.channels)
                for offset_data in constants.other.DISPLACEMENT_OFFSETS_AND_WEIGHTS:
                    new_coords = (x + offset_data[0][0], y + offset_data[0][1])
                    if coords_are_in_image(new_coords, image.size):
                        i2 = coords_to_index(new_coords, image.size, image.channels)
                        offset_pixel = new_pixels[i2:i2 + image.channels]

                        if offset_pixel[-1] < 1.0:
                            if i2 not in displace_data: displace_data[i2] = []
                            displace_data[i2].append((our_pixel, offset_data[1]))

        for i in displace_data:
            data = displace_data[i]

            #final_color = list(new_pixels[i:i + image.channels])

            total_color = [0.0] * image.channels
            total_weight = 0.0

            for composite_data in data:
                weight = composite_data[1]
                total_weight += weight
                for j in range(image.channels - 1):
                    total_color[j] = total_color[j] + (composite_data[0][j] * weight)

            new_color = []
            for j in range(image.channels - 1):
                new_color.append(total_color[j] / total_weight)
            new_color.append(1.0)

            """
            # We composite the original color over the new one.
            aa = final_color[-1]
            ao = 1.0

            for j in range(image.channels - 1):
                ca = final_color[j]
                cb = new_color[j]

                co = ((ca * aa) + (cb * (1 - aa))) / ao

                final_color[j] = co
            final_color[-1] = ao
            """

            new_pixels[i:i + image.channels] = new_color #final_color

        edge_pixels = list(displace_data.keys())

        iteration += 1

    # We're going to copy the colors over but not the alpha values.
    for i in range( 0, image.size[0]*image.size[1]*image.channels, image.channels ):
        old_pixels[i:i+image.channels-1] = new_pixels[i:i+image.channels-1]

    image.pixels[:] = old_pixels
    image.update()


def __objective_function(x,A,B,C,D):
    y = A+B*((x+C)**D)
    return y

__OBJECTIVE_FUNCTION_ESTIMATE = ( 0.0, 1e-6, 0.0, 1.0 )

__OBJECTIVE_FUNCTION_BOUNDS = (
    (0.0, 0.0, 0, 1.0), # min bounds
    (60.0, 1e9, 1e9, 100.0) # max bounds
)


def auto_fill_margin(image, threshold=0.5, num_processes_collect_data=0, num_processes_apply_dilation=0, collect_benchmark_data=False, skip_color_bleed=False):
    # https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow
    # https://stackoverflow.com/questions/8390517/in-python-how-can-i-set-multiple-values-of-a-list-to-zero-simultaneously

    kernel = list(constants.other.DISPLACEMENT_OFFSETS_AND_WEIGHTS)

    benchmark_data = {}
    if collect_benchmark_data:
        benchmark_data["threshold"] = threshold
        benchmark_data["image_size"] = tuple(image.size)
        benchmark_data["image_pixels"] = image.size[0] * image.size[1]
        benchmark_data["image_channels"] = image.channels
        benchmark_data["assigned_num_processes_collect_data"] = num_processes_collect_data
        benchmark_data["assigned_num_processes_apply_dilation"] = num_processes_apply_dilation
        benchmark_data["iterations"] = 0
        benchmark_data["collect_data_data"] = {}
        benchmark_data["collect_data_data"]["times"] = []
        benchmark_data["collect_data_data"]["num_edge_pixels"] = []
        benchmark_data["collect_data_data"]["num_processes"] = []
        benchmark_data["apply_dilation_data"] = {}
        benchmark_data["apply_dilation_data"]["times"] = []
        benchmark_data["apply_dilation_data"]["num_keys"] = []
        benchmark_data["apply_dilation_data"]["num_processes"] = []

    if not skip_color_bleed:
        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Bleeding opaque colors into non-opaque colors...")
        bleed_opaque_into_non_opaque(image)

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Moving pixels over to a pixel holder...")
    pixels_holder = common.general.Holder(multiprocessing.Array(ctypes.c_float, list(image.pixels), lock=False))

    # pixels_holder = common.Holder( list(image.pixels) )

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Filling margin...")
    edge_pixels = multiprocessing.Array(ctypes.c_int64,
                                        range(0, image.size[0] * image.size[1] * image.channels, image.channels),
                                        lock=False)

    last_edge_pixel_count = len(edge_pixels)
    last_delta = 0

    iterations = 0
    while len(edge_pixels) > 0:
        delta = len(edge_pixels) - last_edge_pixel_count
        deltadelta = delta - last_delta

        last_delta = delta

        if constants.other.VERBOSE_LEVEL >= 4:
            common.general.safe_print(" ---- edge pixel count:", len(edge_pixels), " (\U00000394", delta,
                              ", \U00000394\U00000394",
                              deltadelta, ") ", end='')
            constants.other.PRINT_LOCK.acquire()
            sys.stdout.flush()
            constants.other.PRINT_LOCK.release()

        last_edge_pixel_count = len(edge_pixels)

        displace_data = {}

        if constants.other.VERBOSE_LEVEL >= 4:
            common.general.safe_print("collecting data... ", end='')
            constants.other.PRINT_LOCK.acquire()
            sys.stdout.flush()
            constants.other.PRINT_LOCK.release()

        num_processes = num_processes_collect_data
        if num_processes <= 0:
            if constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS is None:
                num_processes = 1 #multiprocessing.cpu_count()
            else:
                x = len(edge_pixels)

                best_num_processes = 1
                best_predicted_time = __objective_function(x, *constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[0][0])

                for i in range(2, len(constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS) + 1):
                    new_predicted_time = __objective_function(x, *constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[i - 1][0])
                    if new_predicted_time < best_predicted_time:
                        best_predicted_time = new_predicted_time
                        best_num_processes = i

                num_processes = best_num_processes

        starttime = time.perf_counter()
        if num_processes == 1:
            outputs = [
                __auto_fill_margin_collect_data(edge_pixels, image.size, image.channels,
                                                pixels_holder.held, kernel, None), ]
        else:
            processes_and_queues = []
            finished_processes_and_queues = []

            if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print("running " + str(num_processes) + "... ", end='')

            for process_number in range(num_processes):
                range_min = (len(edge_pixels) * process_number) // num_processes
                range_max = (len(edge_pixels) * (process_number + 1)) // num_processes
                new_queue = multiprocessing.SimpleQueue()
                new_process = multiprocessing.Process(target=__auto_fill_margin_collect_data,
                                                      args=(edge_pixels[range_min:range_max], tuple(image.size),
                                                            image.channels, pixels_holder.held, kernel, new_queue))
                processes_and_queues.append((new_process, new_queue))
                new_process.start()

            outputs = []

            while len(processes_and_queues) > 0 or len(finished_processes_and_queues) > 0:
                pq_i = len(processes_and_queues) - 1
                while pq_i >= 0:
                    pq = processes_and_queues[pq_i]

                    if not pq[1].empty():
                        result = pq[1].get()
                        if result == 1:
                            pass
                        elif result == 2:
                            finished_processes_and_queues.append(processes_and_queues.pop(pq_i))
                        else:
                            outputs.append(result)

                    pq_i -= 1

                pq_i = len(finished_processes_and_queues) - 1
                while pq_i >= 0:
                    pq = finished_processes_and_queues[pq_i]

                    if not pq[0].is_alive():
                        pq[0].close()
                        pq[1].close()
                        finished_processes_and_queues.pop(pq_i)

                    pq_i -= 1
        endtime = time.perf_counter()
        if collect_benchmark_data:
            benchmark_data["collect_data_data"]["times"].append(endtime - starttime)
            benchmark_data["collect_data_data"]["num_edge_pixels"].append(len(edge_pixels))
            benchmark_data["collect_data_data"]["num_processes"].append(num_processes)

        for output in outputs:
            for i in output:
                if i not in displace_data:
                    displace_data[i] = output[i]
                else:
                    displace_data[i] = displace_data[i] + output[i]

        if constants.other.VERBOSE_LEVEL >= 4:
            common.general.safe_print("applying dilation... ", end='')
            constants.other.PRINT_LOCK.acquire()
            sys.stdout.flush()
            constants.other.PRINT_LOCK.release()

        keys = multiprocessing.Array(ctypes.c_int64, list(displace_data.keys()), lock=False)
        values = list(displace_data.values())

        num_processes = num_processes_apply_dilation
        if num_processes <= 0:
            if constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS is None:
                num_processes = 1 #multiprocessing.cpu_count()
            else:
                x = len(keys)

                best_num_processes = 1
                best_predicted_time = __objective_function(x, *constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[0][1])

                for i in range(2, len(constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS) + 1):
                    new_predicted_time = __objective_function(x, *constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[i - 1][1])
                    if new_predicted_time < best_predicted_time:
                        best_predicted_time = new_predicted_time
                        best_num_processes = i

                num_processes = best_num_processes

        starttime = time.perf_counter()
        if num_processes == 1:
            __auto_fill_margin_apply_dilation(keys, values, image.size, image.channels, pixels_holder.held, threshold)
        else:
            processes_and_queues = []
            finished_processes_and_queues = []

            if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print("running " + str(num_processes) + "... ", end='')

            for process_number in range(num_processes):
                range_min = (len(keys) * process_number) // num_processes
                range_max = (len(keys) * (process_number + 1)) // num_processes
                new_queue = multiprocessing.SimpleQueue()
                new_process = multiprocessing.Process(target=__auto_fill_margin_apply_dilation,
                                                      args=(keys[range_min:range_max], values[range_min:range_max],
                                                            tuple(image.size), image.channels, pixels_holder.held,
                                                            threshold, new_queue))
                processes_and_queues.append((new_process, new_queue))
                new_process.start()

            while len(processes_and_queues) > 0 or len(finished_processes_and_queues) > 0:
                pq_i = len(processes_and_queues) - 1
                while pq_i >= 0:
                    pq = processes_and_queues[pq_i]

                    if not pq[1].empty():
                        result = pq[1].get()
                        if result == 1:
                            pass
                        elif result == 2:
                            finished_processes_and_queues.append(processes_and_queues.pop(pq_i))

                    pq_i -= 1

                pq_i = len(finished_processes_and_queues) - 1
                while pq_i >= 0:
                    pq = finished_processes_and_queues[pq_i]

                    if not pq[0].is_alive():
                        pq[0].close()
                        pq[1].close()
                        finished_processes_and_queues.pop(pq_i)

                    pq_i -= 1
        endtime = time.perf_counter()
        if collect_benchmark_data:
            benchmark_data["apply_dilation_data"]["times"].append(endtime - starttime)
            benchmark_data["apply_dilation_data"]["num_keys"].append(len(displace_data))
            benchmark_data["apply_dilation_data"]["num_processes"].append(num_processes)

        edge_pixels = multiprocessing.Array(ctypes.c_int64, displace_data.keys(), lock=False)

        if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print("Done. Iterations: " + str(iterations))
        iterations += 1

        if collect_benchmark_data:
            benchmark_data["iterations"] = benchmark_data["iterations"] + 1

        """
        name = common.general.clean_filepath(constants.TEXTURE_MISC_FOLDER + "output" + constants.TEXTURE_EXTENSION)

        image.file_format = constants.TEXTURE_FILEFORMAT
        image.filepath_raw = name

        image.update()

        bpy.context.scene.render.image_settings.file_format = constants.TEXTURE_FILEFORMAT
        bpy.context.scene.render.image_settings.color_depth = "8"
        bpy.context.scene.render.image_settings.color_mode = "RGBA"

        image.pixels[:] = pixels_holder.held
        image.update()

        image.save_render(name)
        """

    image.pixels[:] = pixels_holder.held
    image.update()

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Done.")

    if collect_benchmark_data: return benchmark_data
