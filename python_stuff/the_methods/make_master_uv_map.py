import bpy

import common
import constants

import notifications


def run(skip_minimize_stretch=False, skip_final_touches=False, leave_all_selected=False):
    common.general.safe_print("\n")
    common.general.safe_print(" ===   Making Master UV Map   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U0001f310 Making master UV map", is_silent=False)

    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(
            " - Deleting and resetting uv map '" + constants.blender.UV_NAME + "' for everything...")

    for object_name in constants.blender.EVERYTHING:
        obj = bpy.context.view_layer.objects[object_name]

        obj.hide_set(False)
        obj.hide_render = False

        if constants.blender.UV_NAME in obj.data.uv_layers:
            if constants.other.VERBOSE_LEVEL >= 2:
                common.general.safe_print(
                    " -- Deleting uv map '" + constants.blender.UV_NAME + "' from '" + object_name + "'...")
            obj.data.uv_layers.remove(obj.data.uv_layers[constants.blender.UV_NAME])

        if constants.other.VERBOSE_LEVEL >= 2:
            common.general.safe_print(
                " -- Creating blank uv map '" + constants.blender.UV_NAME + "' on '" + object_name + "'...")
        obj.data.uv_layers.new(name=constants.blender.UV_NAME)

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(
            " -- Clearing shapekeys on '" + object_name + "'...")
        bpy.ops.object.shape_key_clear()

    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done setting up blank uv map '" + constants.blender.UV_NAME + "' for everything.")

    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Prepping everything for unwrap...")

    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    for object_name in constants.blender.EVERYTHING:
        if constants.other.VERBOSE_LEVEL >= 2:
            common.general.safe_print(" -- Selecting object '" + object_name + "'...")
        obj = bpy.context.view_layer.objects[object_name]
        obj.select_set(True)

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(
            " -- Setting uv map '" + constants.blender.UV_NAME + "' as active on object '" + object_name + "'...")
        obj.data.uv_layers[constants.blender.UV_NAME].active = True
        obj.data.uv_layers[constants.blender.UV_NAME].active_render = True
        obj.data.uv_layers.active = obj.data.uv_layers[constants.blender.UV_NAME]

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resetting UV maps...")
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.mode_set(mode="EDIT")

    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.reset()
    bpy.ops.uv.pin(clear=True)
    bpy.ops.mesh.select_all(action="SELECT")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Applying custom UV settings...")
    for object_name in constants.blender.EVERYTHING:
        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Object '" + object_name + "'")

        if object_name not in bpy.context.view_layer.objects:
            raise Exception("Attempted to prep object '" + object_name + "' but couldn't find it in this context.")

        obj = bpy.context.view_layer.objects[object_name]

        settings = {}

        if object_name in constants.uv.UV_UNWRAP_SETTINGS:
            settings = constants.uv.UV_UNWRAP_SETTINGS[object_name]

        if obj.data.shape_keys is not None:
            shapekey_name = "Basis"
            if "active_shapekey" in settings:
                shapekey_name = settings["active_shapekey"]

            if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(
                " ---- Setting shape key '" + shapekey_name + " as active.")

            # https://blender.stackexchange.com/a/63433
            keys = obj.data.shape_keys.key_blocks.keys()

            if shapekey_name not in keys:
                if shapekey_name == "Basis":
                    index = 0
                else:
                    raise Exception("Could not find shape key '" + shapekey_name + "' in object '" + object_name + "'.")
            else:
                index = keys.index( shapekey_name )

            obj.active_shape_key_index = index

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Unwrapping...")
    bpy.ops.uv.unwrap(
        method="ANGLE_BASED",
        fill_holes=True,
        correct_aspect=False,
        margin=constants.uv.UV_MARGIN
    )

    if not skip_minimize_stretch:
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Unwrapping done. Minimizing stretch...")

        for i in range(len(constants.blender.EVERYTHING)):
            object_name = constants.blender.EVERYTHING[i]

            if constants.other.VERBOSE_LEVEL >= 2:
                common.general.safe_print(" -- Minimizing stretch for object '" + object_name + "'...")
            obj = bpy.context.view_layer.objects[object_name]

            if constants.other.VERBOSE_LEVEL >= 3:
                common.general.safe_print(" --- Getting uv islands...")

            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Weirdly, has to be in object mode to work.
            islands = common.blender.get_uv_islands(obj)

            if constants.other.VERBOSE_LEVEL >= 3:
                common.general.safe_print(" --- Got the islands. Minimizing stretch now...")

            bpy.ops.object.mode_set(mode="EDIT")

            for island_i in range(len(islands)):
                island = islands[island_i]

                if constants.other.VERBOSE_LEVEL >= 4:
                    common.general.safe_print(" ---- Island", island_i, "/", len(islands))

                bpy.ops.mesh.select_all(action="DESELECT")

                for poly in island:
                    poly.select = True

                    #for loop_index in poly.loop_indices:
                    #    obj.data.uv_layers[constants.blender.UV_NAME].data[loop_index].select = True

                progressprinter = common.general.ProgressPrinter(
                    float(constants.uv.UV_MINIMIZESTRETCH_ITERATIONS), verbose_level=6)
                for k in range(constants.uv.UV_MINIMIZESTRETCH_ITERATIONS):
                    progressprinter.update(k)

                    bpy.ops.uv.minimize_stretch(fill_holes=True,
                                                iterations=constants.uv.UV_MINIMIZESTRETCH_SUBITERATIONS)

                bpy.ops.mesh.select_all(action="DESELECT")

            bpy.ops.object.mode_set(mode="OBJECT")

            for i in range(len(constants.blender.EVERYTHING)):
                object_name = constants.blender.EVERYTHING[i]
                obj = bpy.context.view_layer.objects[object_name]
                obj.select_set(True)

            bpy.ops.object.mode_set(mode="EDIT")

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Stretching minimized.")

    if not skip_final_touches:
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Doing final touches...")

        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=constants.uv.UV_MARGIN, rotate=False)
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=constants.uv.UV_MARGIN, rotate=False)
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=constants.uv.UV_MARGIN, rotate=False)

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Master uv map finished. Resetting...")
    bpy.ops.mesh.select_all(action="DESELECT")

    if leave_all_selected:
        for i in range(len(constants.blender.EVERYTHING)):
            object_name = constants.blender.EVERYTHING[i]
            obj = bpy.context.view_layer.objects[object_name]
            obj.select_set(True)

        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.area.type = "TEXT_EDITOR"

    # bpy.ops.object.select_all(action="DESELECT")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Reset.")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U00002714 Master UV map complete", is_silent=False)
