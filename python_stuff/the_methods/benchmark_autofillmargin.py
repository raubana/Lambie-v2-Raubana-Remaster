import bpy

import os
import time
import random
import json
import datetime
import numpy
import scipy
import scipy.optimize
import matplotlib.pyplot
import matplotlib.patheffects
import multiprocessing

import common
import constants

import notifications


def run(image_sizes=None, combos="SIMPLE", writetofile=True):
    common.general.safe_print("")
    common.general.safe_print(" ===   Benchmarking auto_fill_margin   === ")

    if notifications.constants.ENABLED:
        notifications.constants.HANDLER.add_notification( "\U000023f1 Benchmarking auto_fill_margin", is_silent=False)

    if image_sizes is None:
        image_sizes = [(2048,2048),]

    max_processes = multiprocessing.cpu_count()

    combinations = []

    if combos == "MIN":
        combinations.append((1, 1))
    elif combos == "MAX":
        combinations.append((max_processes, max_processes))
    elif combos == "SIMPLE":
        for x in range(1, max_processes + 1):
            combinations.append((x, x))
    elif combos == "SMART":
        for x in range(2, max_processes + 1):
            combinations.append((1, x))
            combinations.append((x, 1))
    elif combos == "ALL":
        for num_processes_collect_data in range(1, max_processes + 1):
            for num_processes_apply_dilation in range(1, max_processes + 1):
                combinations.append((num_processes_collect_data, num_processes_apply_dilation))
    elif type(combos) in (list, tuple):
        combinations = combos
    else:
        raise Exception("benchmark_auto_fill_margin received a weird value for 'combos'")

    for image_size in image_sizes:
        output_file = None
        if writetofile:
            output_file = open(os.path.dirname(__file__) + "/benchmark.txt", 'a', encoding="utf-8")

        stopwatch_results = []

        for combination in combinations:
            num_processes_collect_data = combination[0]
            num_processes_apply_dilation = combination[1]

            bpy.ops.image.open(
                allow_path_tokens=True,
                filepath=constants.texture.TEXTURE_MISC_FOLDER + "autofillmargin_benchmarker" + constants.texture.TEXTURE_EXTENSION,
                relative_path=True
            )

            img = bpy.context.blend_data.images["autofillmargin_benchmarker" + constants.texture.TEXTURE_EXTENSION]

            if image_size is None:
                image_size = img.size
            if image_size[0] != img.size[0] or image_size[1] != img.size[1]:
                img.scale(image_size[0], image_size[1])

            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - TESTING", num_processes_collect_data, num_processes_apply_dilation, image_size)

            starttime = time.perf_counter()
            benchmark_data = common.texture.auto_fill_margin(img,
                             threshold=0.5,
                             num_processes_collect_data=num_processes_collect_data,
                             num_processes_apply_dilation=num_processes_apply_dilation,
                             collect_benchmark_data = True)
            finishtime = time.perf_counter()

            diftime = finishtime - starttime

            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - time:", str(datetime.timedelta(seconds=diftime)))

            if notifications.constants.ENABLED:
                notifications.constants.HANDLER.add_notification(" - \U00002714 " + str(datetime.timedelta(seconds=diftime)),
                                                       add_datetime=False)

            stopwatch_results.append((diftime, num_processes_collect_data, num_processes_apply_dilation))

            if writetofile:
                output_file.write( json.dumps(benchmark_data, indent=4) )
                output_file.write( "\n" )

            bpy.context.blend_data.images.remove(img)

        stopwatch_results.sort(key=lambda x: x[0])

        stopwatch_results_message = ""
        total = 0.0
        for i in range(len(stopwatch_results)):
            stopwatch_result = stopwatch_results[i]
            stopwatch_results_message += str(i + 1) + ".\t " + str(stopwatch_result[1]) + "\t " +\
                                         str(stopwatch_result[2]) + "\t time: " +\
                                         str(datetime.timedelta(seconds=stopwatch_result[0]))
            if i < len(stopwatch_results) - 1: stopwatch_results_message += "\n"
            total += stopwatch_result[0]
        stopwatch_results_message += "\n\ntotal: " + str(datetime.timedelta(seconds=total)) + "\n"

        common.general.safe_print("")
        common.general.safe_print("RESULTS: " + str(image_size) + "\n")
        common.general.safe_print(stopwatch_results_message)
        common.general.safe_print("")

        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification(
                "\U00002611 Benchmark Complete " + str(image_size) + "\n\n" + stopwatch_results_message, is_silent=False)

        if writetofile:
            output_file.close()

            common.general.safe_print("\n\n\n\n\nThe benchmark data was written to 'benchmark.txt'.")
            common.general.safe_print("If it already existed, the new data was added to the end of the file.\n\n\n\n\n")


def load_data():
    if os.path.exists(os.path.dirname(__file__) + "/benchmark.txt"):
        benchmark_file = open(os.path.dirname(__file__) + "/benchmark.txt", "r", encoding="utf-8")

        depth = 0
        current_json_text = ""

        all_json_text = []

        break_out = False
        for line in benchmark_file:
            for ch in line:
                if ch == '{':
                    depth += 1
                    if depth == 1:
                        current_json_text = ""
                elif ch == '}':
                    depth -= 1
                    if depth < 0:
                        raise Exception(
                            "Attempted to parse benchmark.txt but found at least one unmatched close brace.")
                    elif depth == 0:
                        current_json_text += "}"
                        all_json_text.append(current_json_text)
                        current_json_text = ""

                if depth > 0:
                    current_json_text += ch

        if depth > 0:
            raise Exception("Attempted to parse benchmark.txt but found at least one unmatched open brace.")

        all_data = []

        for json_text in all_json_text:
            data = json.loads(json_text)
            all_data.append(data)

        return all_data
    else:
        raise Exception("Attempted to load benchmark.txt, but it does not exist.")


def calculate_bestfit_parameters_for_data(data_x, data_y):
    data_x = numpy.asarray( data_x )
    data_y = numpy.asarray( data_y )

    data_parameters, data_covariance = scipy.optimize.curve_fit(
        common.texture.__objective_function,
        data_x,
        data_y,
        p0=common.texture.__OBJECTIVE_FUNCTION_ESTIMATE,
        bounds=common.texture.__OBJECTIVE_FUNCTION_BOUNDS
    )

    return data_parameters


def calculate_bestfit_parameters_for_all_data(all_data):
    output = []

    for data in all_data:
        collect_data_parameters = calculate_bestfit_parameters_for_data(
            data["collect_data_data"]["num_edge_pixels"][3:-3],
            data["collect_data_data"]["times"][3:-3]
        )
        apply_dilation_parameters = calculate_bestfit_parameters_for_data(
            data["apply_dilation_data"]["num_keys"][3:-3],
            data["apply_dilation_data"]["times"][3:-3]
        )

        output.append( (collect_data_parameters, apply_dilation_parameters) )

    return output


def generate_bestfit_parameters(prettyprintresults=True):
    all_data = load_data()
    all_parameters = calculate_bestfit_parameters_for_all_data(all_data)

    if prettyprintresults:
        common.general.safe_print("\n\n\n\n\nYOUR PARAMETERS:\n")

        common.general.safe_print("(")

        for i in range(len(all_parameters)):
            common.general.safe_print("\t(", end='')

            parameters_group = all_parameters[i]
            for j in range(len(parameters_group)):
                if j > 0:
                    common.general.safe_print("\t", end='')
                common.general.safe_print(str(tuple(parameters_group[j])), end='')
                common.general.safe_print(",", end='')
                if j < len(parameters_group)-1:
                    common.general.safe_print("")

            common.general.safe_print("),", end='')
            common.general.safe_print("")

        common.general.safe_print(")\n")

        common.general.safe_print("Copy and paste this after 'AUTOFILLMARGIN_BENCHMARK_PARAMETERS = ' in 'constants/bake.py'.")
        common.general.safe_print("The extra commas are weird, I know, but they're important.\n\n\n\n\n")

    return all_parameters


def plot_results(show_curves=True, load_benchmark=True, show_ideal=True):
    matplotlib.pyplot.grid(True, ls=":")

    marker_styles = ('.', 'x', '+', '*', '1', '2', '3', '4')
    colors = ("red", "orange", "yellow", "green", "cyan", "blue", "purple", "black", "pink", "brown")

    min_x = 0
    min_y = 0.0
    max_x = 1000000
    max_y = 5.0

    if load_benchmark:
        all_data = load_data()

        color_index = 0
        marker_style_index = 0
        for data in all_data:
            collect_data_x = numpy.asarray(data["collect_data_data"]["num_edge_pixels"])
            collect_data_y = numpy.asarray(data["collect_data_data"]["times"])
            apply_dilation_x = numpy.asarray(data["apply_dilation_data"]["num_keys"])
            apply_dilation_y = numpy.asarray(data["apply_dilation_data"]["times"])

            min_x = min(min_x, min(collect_data_x), min(apply_dilation_x))
            min_y = min(min_y, min(collect_data_y), min(apply_dilation_y))
            max_x = max(max_x, max(collect_data_x), max(apply_dilation_x))
            max_y = max(max_y, max(collect_data_y), max(apply_dilation_y))

            matplotlib.pyplot.scatter(collect_data_x, collect_data_y, color=colors[color_index], marker=marker_styles[marker_style_index], alpha=0.25)
            color_index = (color_index + 1) % len(colors)
            marker_style_index = (marker_style_index+1)%len(marker_styles)

            matplotlib.pyplot.scatter(apply_dilation_x, apply_dilation_y, color=colors[color_index], marker=marker_styles[marker_style_index], alpha=0.25)
            color_index = (color_index + 1) % len(colors)
            marker_style_index = (marker_style_index + 1) % len(marker_styles)

    curve_x = numpy.linspace(min_x, max_x, 10000)

    if show_curves:
        for i in range(len(constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS)):
            collect_data_curve = common.texture.__objective_function(curve_x, *
                constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[i][0])
            apply_dilation_curve = common.texture.__objective_function(curve_x, *
                constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[i][1])

            min_y = min( min_y, min(collect_data_curve), min(collect_data_curve) )
            max_y = max( max_y, max(collect_data_curve), max(apply_dilation_curve) )

        if show_ideal:
            min_collect_data_curve = numpy.linspace(max_y, max_y, 10000)
            min_apply_dilation_curve = numpy.linspace(max_y, max_y, 10000)

        color_index = 0
        for i in range(len(constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS)):
            collect_data_curve = common.texture.__objective_function(curve_x, *constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[i][0])
            matplotlib.pyplot.plot(
                curve_x,
                collect_data_curve,
                label=f"collect {i+1}",
                color=colors[color_index],
                lw=2.0,
                ls="-",
                alpha=1.0,
                path_effects=[
                    matplotlib.patheffects.SimpleLineShadow(shadow_color="black", offset=(0.5, -0.5), linewidth=7.0, alpha=0.3),
                    matplotlib.patheffects.SimpleLineShadow(shadow_color="white", offset=(0.0, -0.0), linewidth=4.0, alpha=0.8),
                    matplotlib.patheffects.Normal()
                ]
            )
            color_index = (color_index+1)%len(colors)

            apply_dilation_curve = common.texture.__objective_function(curve_x, *constants.bake.AUTOFILLMARGIN_BENCHMARK_PARAMETERS[i][1])
            matplotlib.pyplot.plot(
                curve_x,
                apply_dilation_curve,
                label=f"apply {i+1}",
                color=colors[color_index],
                lw=2.0,
                ls="-",
                alpha=1.0,
                path_effects=[
                    matplotlib.patheffects.SimpleLineShadow(shadow_color="black", offset=(0.5, -0.5), linewidth=7.0, alpha=0.3),
                    matplotlib.patheffects.SimpleLineShadow(shadow_color="white", offset=(0.0, -0.0), linewidth=4.0, alpha=0.8),
                    matplotlib.patheffects.Normal()
                ]
            )
            color_index = (color_index + 1) % len(colors)

            if show_ideal:
                min_collect_data_curve = numpy.minimum(min_collect_data_curve, collect_data_curve)
                min_apply_dilation_curve = numpy.minimum(min_apply_dilation_curve, apply_dilation_curve)

        if show_ideal:
            matplotlib.pyplot.plot(
                curve_x,
                min_collect_data_curve,
                label=f"collect ideal",
                color=colors[color_index],
                lw=4.0,
                ls=":",
                alpha=1.0
            )
            color_index = (color_index + 1) % len(colors)

            matplotlib.pyplot.plot(
                curve_x,
                min_apply_dilation_curve,
                label=f"apply ideal",
                color=colors[color_index],
                lw=4.0,
                ls=":",
                alpha=1.0
            )
            color_index = (color_index + 1) % len(colors)

    matplotlib.pyplot.xlabel("# Edge Pixels / # Keys")
    matplotlib.pyplot.ylabel("Time (s)")
    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()