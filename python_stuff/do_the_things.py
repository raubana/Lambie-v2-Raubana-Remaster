import traceback

import bpy

import common as com
import common.texture
import constants as const
import notifications as notif
import the_methods as tm


def do_the_things():
    if notif.constants.ENABLED: notif.constants.HANDLER.add_notification("\U000025b6 doTheThings STARTED", is_silent=False)

    com.general.safe_print(" ===== DOING THE THINGS! ===== ")

    tm.reset_everything.run()

    # --------- BENCHMARKING (to make auto_fill_margin go a little faster) ---------
    #tm.benchmark_autofillmargin.run() # do this first. should only need to run this once unless you expect different results. don't forget to delete benchmark.txt!
    #tm.benchmark_autofillmargin.plot_results(show_curves=False) # optional. will show the results of your benchmark on a graph.
    #tm.benchmark_autofillmargin.generate_bestfit_parameters() # do this second. follow directions in the console.
    #tm.benchmark_autofillmargin.plot_results(load_benchmark=True, show_ideal=False) # optional. will show your benchmark and curves.
    #tm.benchmark_autofillmargin.run(image_sizes=((1024,1024),), combos=((1,1),(0,0)), writetofile=False) # optional race. will compare a baseline to your benchmark curves.

    # --------- UV Map Generation and Optimization ---------

    # Minimize Stretch feature isn't working as intended right now. Skip the step to save time.
    # Both instances of leave_all_selected haven't been working right either.

    #tm.make_master_uv_map.run(skip_minimize_stretch=True, skip_final_touches=False, leave_all_selected=False)

    #tm.use_physics_to_optimize_master_uv_map.run(skip_mixing=False, skip_shaking_up=False, skip_scaling=False,
    #                                             skip_maximize_radius=False, auto_apply=False, leave_all_selected=False)

    # --------- Baking ---------
    #tm.bake.ao.run(skip_pp=False)

    #com.blender.load_ao()

    #tm.bake.generic.albedo(skip_pp=False)
    #tm.bake.generic.specular(skip_pp=False)
    #tm.bake.generic.smoothness(skip_pp=False)
    #tm.merge_specular_and_smoothness.run()
    #tm.bake.generic.emissions(skip_pp=False)
    #tm.bake.generic.normals(skip_pp=False)

    #tm.reset_everything.run()

    # --------- Exporting ---------
    # MAKE SURE THE CONSOLE IS OPENED FOR THIS PART.
    #tm.do_final_export.run(skip_warning=False, merge_meshes=True)

    com.general.safe_print(" ===== DONE DOING THE THINGS! ===== ")

    if notif.constants.ENABLED: notif.constants.HANDLER.add_notification("\U00002705 doTheThings FINISHED", is_silent=False)


def run():
    notif.init()

    try:
        do_the_things()
    except Exception as e:
        error_message = traceback.format_exc()
        com.general.safe_print(error_message)
        if notif.constants.ENABLED: notif.constants.HANDLER.add_notification(
            "\U0000274c The doTheThings method raised an exception:\n" + error_message, is_silent=False)

    notif.quit()