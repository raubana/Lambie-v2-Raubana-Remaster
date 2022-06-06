import os
import math
import PIL.Image

import bpy
import mathutils

import common
import constants

import notifications


def run(skip_pp=False):
    common.general.safe_print("\n")
    common.general.safe_print(" ===   Baking Ambient Occlusion   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("\U0001f4a1 Baking AO", is_silent=False)

    if bpy.context.scene.render.engine != "CYCLES":
        raise Exception("Can't bake AO in this render engine. Must be set to Cycles.")

    num_samples = constants.bake.AO_CYCLES_SAMPLES
    if constants.bake.AO_CYCLES_BAD_MSAA:
        num_samples = int(math.ceil(num_samples / (constants.bake.AO_CYCLES_BAD_MSAA_SCALE**2)))

    bpy.context.scene.cycles.samples = num_samples

    bpy.context.scene.cycles.diffuse_bounces = constants.bake.AO_CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.glossy_bounces = 0
    bpy.context.scene.cycles.transmission_bounces = 0
    bpy.context.scene.cycles.volume_bounces = 0
    bpy.context.scene.cycles.transparent_max_bounces = 0
    bpy.context.scene.cycles.max_bounces = constants.bake.AO_CYCLES_MAXBOUNCES

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Creating AO texture '" + constants.texture.TEXTURE_AO_NAME + "'...")
    size = constants.texture.AO_TEXTURE_SIZE
    if constants.bake.AO_CYCLES_BAD_MSAA:
        size = (constants.texture.AO_TEXTURE_SIZE[0] * constants.bake.AO_CYCLES_BAD_MSAA_SCALE, constants.texture.AO_TEXTURE_SIZE[1] * constants.bake.AO_CYCLES_BAD_MSAA_SCALE)

    num_tiles = [1, 1]
    if constants.bake.AO_CYCLES_STITCHING:
        num_tiles = [
            int(math.ceil(size[0] / constants.bake.AO_CYCLES_STITCHING_TILESIZE)),
            int(math.ceil(size[1] / constants.bake.AO_CYCLES_STITCHING_TILESIZE))
        ]

    margin = constants.bake.AO_TEXTURE_BAKINGMARGIN
    if margin == -1:
        if constants.bake.AO_CYCLES_STITCHING:
            margin = constants.bake.AO_CYCLES_STITCHING_TILESIZE
        else:
            margin = min(constants.texture.AO_TEXTURE_SIZE)
        margin *= constants.uv.UV_MARGIN
    if constants.bake.AO_CYCLES_BAD_MSAA:
        margin *= constants.bake.AO_CYCLES_BAD_MSAA_SCALE
    margin = int(math.floor(margin)) - 1
    if margin < 0: margin = 0

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - MARGIN:", margin)

    tile_texture = None
    for tile_y in range(num_tiles[1]):
        for tile_x in range(num_tiles[0]):
            if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
                " - \U000025A6 TILE ["+str(tile_x)+"/"+str(num_tiles[0])+", "+str(tile_y)+"/"+str(num_tiles[1])+"]")

            if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print("\n -- TILE:", tile_x, ",", tile_y)

            tile_uvmap_name = constants.blender.UV_NAME
            tile_name = constants.texture.TEXTURE_AO_NAME + constants.texture.TEXTURE_EXTENSION
            tile_dims = list(size)
            if constants.bake.AO_CYCLES_STITCHING:
                tile_uvmap_name = "TEMP_UVMap"

                tile_name = "TEMP_tile_" + str(tile_x) + "_" + str(tile_y) + constants.texture.TEXTURE_EXTENSION

                tile_dims = [constants.bake.AO_CYCLES_STITCHING_TILESIZE, constants.bake.AO_CYCLES_STITCHING_TILESIZE]

                if tile_x == num_tiles[0] - 1:
                    xmod = size[0] % constants.bake.AO_CYCLES_STITCHING_TILESIZE
                    if xmod > 0: tile_dims[0] = xmod

                if tile_y == num_tiles[1] - 1:
                    ymod = size[1] % constants.bake.AO_CYCLES_STITCHING_TILESIZE
                    if ymod > 0: tile_dims[1] = ymod

            if tile_texture is None:
                tile_texture = common.texture.make_blank_image(tile_name, tile_dims, fill_color=(0.5,0.5,0.5,0.0))

            if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- AO texture created. Prepping to bake... ")

            # The UV system uses the typical coordinate system most people know, where +x is right and +y is UP.
            # In other words, the origin is in the BOTTOM-left.

            # However, PIL uses the computer standard, where +x is right and +y is DOWN.
            # In other words, the origin is in the TOP-left.

            # For the sake of consistency, I'm going to force PIL to act like it uses the typical coordinate system
            # standard, so stitching will be much easier.

            m = mathutils.Matrix.Translation((
                -(tile_x * constants.bake.AO_CYCLES_STITCHING_TILESIZE) / float(size[0]),
                -(tile_y * constants.bake.AO_CYCLES_STITCHING_TILESIZE) / float(size[1]),
                0.0
            ))

            m = mathutils.Matrix.Scale(
                size[0] / float(tile_dims[0]),
                4, mathutils.Vector((1, 0, 0))) @ m

            m = mathutils.Matrix.Scale(
                size[1] / float(tile_dims[1]),
                4, mathutils.Vector((0, 1, 0))) @ m

            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Prepping armature '" + constants.blender.ARMATURE_NAME + "'")
            if not constants.blender.ARMATURE_NAME in bpy.context.view_layer.objects:
                raise Exception(
                    "Attempted to prep armature '" + constants.blender.ARMATURE_NAME + "' before batch baking AO but couldn't find it in this context.")
            armature = bpy.context.view_layer.objects[constants.blender.ARMATURE_NAME]

            armature.hide_set(False)
            armature.hide_viewport = False
            armature.hide_render = True

            obj_has_uv_in_bounds = {}

            for object_name in constants.blender.EVERYTHING:
                obj_has_uv_in_bounds[object_name] = True

            for object_name in constants.blender.EVERYTHING:
                if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(
                    " --- Prepping object '" + object_name + "'...")
                if object_name not in bpy.context.view_layer.objects:
                    raise Exception(
                        "Attempted to prep object '" + object_name + "' before batch baking but couldn't find it in this context.")
                obj = bpy.context.view_layer.objects[object_name]

                obj.hide_set(False)
                obj.hide_render = True

                bpy.ops.object.select_all(action="DESELECT")

                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

                bpy.ops.object.shape_key_clear()

                bpy.ops.object.select_all(action="DESELECT")

                if constants.blender.UV_NAME not in obj.data.uv_layers:
                    raise Exception(
                        "Object '" + object_name + "' lacks the expected UV map named '" + constants.blender.UV_NAME + "'")
                else:
                    original_uvmap = obj.data.uv_layers[constants.blender.UV_NAME]

                    obj.data.uv_layers.active = original_uvmap

                    if constants.bake.AO_CYCLES_STITCHING:
                        obj_has_uv_in_bounds[object_name] = False

                        if "TEMP_UVMap" in obj.data.uv_layers:
                            obj.data.uv_layers.remove(obj.data.uv_layers["TEMP_UVMap"])

                        temp_uvmap = obj.data.uv_layers.new(name="TEMP_UVMap", do_init=True)

                        obj.data.uv_layers.active = temp_uvmap

                        # Translate and scale the UV coords so they're setup for the tile.
                        for uvloop in temp_uvmap.data:
                            new_uv = m @ mathutils.Vector((uvloop.uv.x, uvloop.uv.y, 0.0))

                            uvloop.uv.x = new_uv.x
                            uvloop.uv.y = new_uv.y

                        islands = common.blender.get_uv_islands(obj)

                        for island in islands:
                            for poly in island:
                                loop_start_index = poly.loop_start
                                loop_total = poly.loop_total

                                uv = temp_uvmap.data[loop_start_index].uv

                                min_x = uv.x
                                min_y = uv.y
                                max_x = uv.x
                                max_y = uv.y

                                for loop_index in range(loop_start_index+1, loop_start_index+loop_total):
                                    uv = temp_uvmap.data[loop_index].uv

                                    min_x = min(min_x, uv.x)
                                    min_y = min(min_y, uv.y)
                                    max_x = max(max_x, uv.x)
                                    max_y = max(max_y, uv.y)

                                min_x = min_x*tile_dims[0] - margin
                                min_y = min_y*tile_dims[1] - margin
                                max_x = max_x*tile_dims[0] + margin
                                max_y = max_y*tile_dims[1] + margin

                                # https://www.geeksforgeeks.org/find-two-rectangles-overlap/
                                if not (max_x < 0 or min_x > tile_dims[0] or min_y < 0 or max_y > tile_dims[1]):
                                    obj_has_uv_in_bounds[object_name] = True
                                    break

                            if obj_has_uv_in_bounds[object_name]:
                                break

                        obj.data.uv_layers.active = original_uvmap

            if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- All prepped. Commencing AO baking...")
            for target_object_name in constants.blender.EVERYTHING:
                if obj_has_uv_in_bounds[target_object_name] is not True:
                    if constants.other.VERBOSE_LEVEL >= 3:
                        common.general.safe_print(" --- Object '" + target_object_name + "' not in tile...")
                    continue # We skip objects that won't show up on the tile.

                #if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
                #    " -- \U0001f526  Baking AO for object '" + target_object_name)

                if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Object '" + target_object_name + "'")

                obj = bpy.context.view_layer.objects[target_object_name]

                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Generating settings...")
                settings = dict(constants.bake.AO_DEFAULTSETTINGS)

                if target_object_name in constants.bake.AO_SETTINGS:
                    for custom_setting_key in constants.bake.AO_SETTINGS[target_object_name]:
                        if custom_setting_key == "enabled" or custom_setting_key == "disabled":
                            if custom_setting_key in settings:
                                settings[custom_setting_key] = settings[custom_setting_key].union(
                                    constants.bake.AO_SETTINGS[target_object_name][custom_setting_key])
                            else:
                                settings[custom_setting_key] = constants.bake.AO_SETTINGS[target_object_name][custom_setting_key]
                        elif custom_setting_key == "shapekeys":
                            if "shapekeys" in settings:
                                settings["shapekeys"] = settings["shapekeys"] | constants.bake.AO_SETTINGS[target_object_name]["shapekeys"]
                            else:
                                settings["shapekeys"] = dict(constants.bake.AO_SETTINGS[target_object_name]["shapekeys"])
                        elif custom_setting_key == "pose" or custom_setting_key == "skip":
                            settings[custom_setting_key] = constants.bake.AO_SETTINGS[target_object_name][custom_setting_key]
                        else:
                            raise Exception(
                                "Object '" + target_object_name + "' had a custom setting with key named '" + custom_setting_key + "' which is not recognized!")

                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Settings generated.")

                if "skip" in settings and settings["skip"] is True:
                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Object marked to be skipped. Skipping.")
                else:
                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Prepping target object's material...")

                    # https://blender.stackexchange.com/questions/23436/control-cycles-eevee-material-nodes-and-material-properties-using-python/23446
                    mat = obj.active_material
                    if mat is None:
                        raise Exception("Object '" + target_object_name + "' has no active material.")

                    common.blender.set_output_in_general_shader(obj, mat, "DiffuseShader")

                    bpy.ops.object.select_all(action="DESELECT")
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj

                    bpy.context.area.type = "NODE_EDITOR"

                    uvmap_node = mat.node_tree.nodes.new(type='ShaderNodeUVMap')
                    tex_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')

                    uvmap_node.uv_map = constants.blender.UV_NAME
                    tex_node.image = tile_texture

                    mat.node_tree.links.new(uvmap_node.outputs[0], tex_node.inputs[0])

                    bpy.ops.node.select_all(action="DESELECT")
                    tex_node.select = True
                    mat.node_tree.nodes.active = tex_node

                    bpy.context.area.type = "TEXT_EDITOR"

                    bpy.ops.object.select_all(action="DESELECT")

                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Material prepped. Applying settings...")

                    # First we set up this object, because... I mean, duh.
                    obj.hide_render = False

                    # Then the armature.
                    bpy.ops.object.select_all(action="DESELECT")
                    armature.select_set(True)
                    bpy.context.view_layer.objects.active = armature

                    bpy.ops.object.mode_set(mode="POSE")

                    bpy.ops.pose.select_all(action='SELECT')

                    bpy.ops.pose.transforms_clear()

                    bpy.ops.object.mode_set(mode="OBJECT")

                    bpy.ops.object.select_all(action="DESELECT")

                    # Then we enable anything in "enabled" that isn't also in "disabled".
                    if "enabled" in settings:
                        for key in settings["enabled"]:
                            if "disabled" not in settings or key not in settings["disabled"]:
                                if key not in bpy.context.view_layer.objects:
                                    raise Exception(
                                        "Attempted to enable object '" + key + "' before baking AO for object '" + target_object_name + "' but couldn't find it in this context.")
                                obj2 = bpy.context.view_layer.objects[key]
                                obj2.hide_render = False
                                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Enabled '" + key + "'")

                    # Next we set the shape keys.
                    if "shapekeys" in settings:
                        for key in settings["shapekeys"]:
                            if key not in bpy.context.view_layer.objects:
                                raise Exception(
                                    "Was about to modify shape keys on object '" + key + "' before baking AO for object '" + target_object_name + "' but couldn't find it in this context.")
                            obj2 = bpy.context.view_layer.objects[key]
                            for key2 in settings["shapekeys"][key]:
                                if key2 not in obj2.data.shape_keys.key_blocks:
                                    raise Exception(
                                        "Attempted to modify shape key '" + key2 + "' on object '" + key + "' before baking AO for object '" + target_object_name + "' but couldn't find it.")
                                new_value = settings["shapekeys"][key][key2]
                                if type(new_value) is not float:
                                    raise Exception(
                                        "Was about to modify shape key '" + key2 + "' on object '" + key + "' before baking AO for object '" + target_object_name + "' but the value given is not in the form of a float.")
                                obj2.data.shape_keys.key_blocks[key2].value = new_value
                                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(
                                    " ---- Shape key '" + key2 + "' set to '" + str(new_value) + "' on object '" + key + "'")

                    # Then we set the pose.
                    if "pose" in settings:
                        poselib = armature.pose_library
                        if poselib is None:
                            raise Exception(
                                "Was about to set a pose to armature '" + constants.blender.ARMATURE_NAME + "' before baking AO for object '" + target_object_name + "' but the armature doesn't have one.")
                        if settings["pose"] not in poselib.pose_markers:
                            raise Exception("Attempted to apply pose '" + settings[
                                "pose"] + "' to armature '" + constants.blender.ARMATURE_NAME + "' before baking AO for object '" + target_object_name + "' but the pose doesn't exist.")

                        bpy.ops.object.select_all(action="DESELECT")

                        armature.select_set(True)
                        bpy.context.view_layer.objects.active = armature

                        bpy.ops.object.mode_set(mode="POSE")

                        bpy.ops.pose.select_all(action='SELECT')

                        keys = poselib.pose_markers.keys()
                        pose_name = settings["pose"]
                        pose_i = keys.index(pose_name)

                        bpy.ops.poselib.apply_pose(pose_index=pose_i)
                        if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(
                            " ---- Armature '" + constants.blender.ARMATURE_NAME + "' set to pose '" + settings["pose"] + "'.")

                        bpy.ops.object.mode_set(mode="OBJECT")

                        bpy.ops.object.select_all(action="DESELECT")

                    # Deselecting everything and selecting our target object.
                    bpy.ops.object.select_all(action='DESELECT')

                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj

                    # Now we bake!
                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Settings applied. Baking AO...")

                    bpy.ops.object.bake(
                        type="AO",
                        pass_filter={"DIFFUSE"},
                        target="IMAGE_TEXTURES",
                        save_mode="INTERNAL",
                        margin=margin,
                        margin_type=constants.bake.AO_TEXTURE_BAKINGMARGIN_TYPE,
                        uv_layer=tile_uvmap_name
                    )

                    common.texture.save_image(
                        bpy.context.blend_data.images[tile_name],
                        "RGBA",
                        "16",
                        delete_from_memory=False
                    )

                    # Gotta reset now that baking is finished for this object.
                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Done baking AO. Resetting...")

                    bpy.ops.object.select_all(action="DESELECT")

                    armature.select_set(True)
                    bpy.context.view_layer.objects.active = armature

                    bpy.ops.object.mode_set(mode="POSE")

                    bpy.ops.pose.select_all(action='SELECT')

                    bpy.ops.pose.transforms_clear()

                    bpy.ops.object.mode_set(mode="OBJECT")

                    bpy.ops.object.select_all(action="DESELECT")

                    if "shapekeys" in settings:
                        for key in settings["shapekeys"]:
                            obj2 = bpy.context.view_layer.objects[key]

                            bpy.ops.object.select_all(action="DESELECT")

                            obj2.select_set(True)
                            bpy.context.view_layer.objects.active = obj2

                            bpy.ops.object.shape_key_clear()

                            bpy.ops.object.select_all(action="DESELECT")

                    if "enabled" in settings:
                        for key in settings["enabled"]:
                            if "disabled" not in settings or key not in settings["disabled"]:
                                obj2 = bpy.context.view_layer.objects[key]

                                obj2.hide_render = True

                    bpy.ops.object.select_all(action="DESELECT")
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj

                    bpy.context.area.type = "NODE_EDITOR"

                    mat.node_tree.nodes.remove(uvmap_node)
                    mat.node_tree.nodes.remove(tex_node)

                    bpy.context.area.type = "TEXT_EDITOR"

                    bpy.ops.object.select_all(action="DESELECT")

                    obj.hide_render = True

                    if constants.bake.AO_CYCLES_STITCHING:
                        obj.data.uv_layers.remove(obj.data.uv_layers["TEMP_UVMap"])

                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Reset.")

            if constants.bake.AO_CYCLES_STITCHING:
                bpy.context.blend_data.images.remove(tile_texture)
                tile_texture = None

    if tile_texture is not None:
        bpy.context.blend_data.images.remove(tile_texture)
        del tile_texture

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print("\n - AO baking done for all objects.")

    if constants.bake.AO_CYCLES_STITCHING:
        #https://stackoverflow.com/questions/10657383/stitching-photos-together

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Stitching tiles...")

        new_fill_color = []
        for channel in (0.5,0.5,0.5,0.0): # I'm being lazy at the moment...
            new_fill_color.append(int(channel))
        new_fill_color[-1] = 0
        new_fill_color = tuple(new_fill_color)

        final_image = PIL.Image.new("RGBA", size, new_fill_color)

        last_tile_dims = [
            int(size[0] % constants.bake.AO_CYCLES_STITCHING_TILESIZE),
            int(size[1] % constants.bake.AO_CYCLES_STITCHING_TILESIZE)
        ]

        if last_tile_dims[0] == 0: last_tile_dims[0] = constants.bake.AO_CYCLES_STITCHING_TILESIZE
        if last_tile_dims[1] == 0: last_tile_dims[1] = constants.bake.AO_CYCLES_STITCHING_TILESIZE

        for tile_y in range(num_tiles[1]):
            for tile_x in range(num_tiles[0]):
                tile_name = "TEMP_tile_" + str(tile_x) + "_" + str(tile_y) + constants.texture.TEXTURE_EXTENSION

                if os.path.isfile(constants.texture.TEXTURE_BAKED_FOLDER + tile_name):
                    tile = PIL.Image.open(constants.texture.TEXTURE_BAKED_FOLDER + tile_name)

                    pos = [
                        tile_x * constants.bake.AO_CYCLES_STITCHING_TILESIZE,
                        size[1] - (tile_y * constants.bake.AO_CYCLES_STITCHING_TILESIZE) - last_tile_dims[1]
                    ]

                    final_image.paste(tile, tuple(pos))

                    del tile
                else:
                    if constants.other.VERBOSE_LEVEL >= 2:
                        common.general.safe_print(" -- could not find file: " + tile_name)

        #if constants.bake.AO_CYCLES_BAD_MSAA:
        #    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resizing...")
        #    final_image = final_image.resize(constants.texture.TEXTURE_SIZE, resample=PIL.Image.Resampling.LANCZOS)

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Saving final image...")
        final_image.save(
            constants.texture.TEXTURE_BAKED_FOLDER +
            constants.texture.TEXTURE_AO_NAME +
            constants.texture.TEXTURE_EXTENSION
        )

        del final_image

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Cleaning up tile images...")

        for tile_y in range(num_tiles[1]):
            for tile_x in range(num_tiles[0]):
                tile_name = "TEMP_tile_" + str(tile_x) + "_" + str(tile_y) + constants.texture.TEXTURE_EXTENSION

                common.general.safely_delete_file(constants.texture.TEXTURE_BAKED_FOLDER + tile_name)

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Loading AO texture back into memory...")

    bpy.ops.image.open(
        allow_path_tokens=True,
        filepath=constants.texture.TEXTURE_BAKED_FOLDER +
            constants.texture.TEXTURE_AO_NAME +
            constants.texture.TEXTURE_EXTENSION,
        relative_path=True
    )

    target_texture = bpy.context.blend_data.images[
        constants.texture.TEXTURE_AO_NAME+constants.texture.TEXTURE_EXTENSION
    ]

    if not skip_pp:
        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification("\U0001f51c Finished baking AO, finishing up")

        if constants.bake.AO_CYCLES_BAD_MSAA:
            if notifications.constants.ENABLED:
                notifications.constants.HANDLER.add_notification(" - \U000025F0 Resizing (Bad MSAA)...")
            if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resizing (Bad MSAA)...")
            target_texture.scale(constants.texture.AO_TEXTURE_SIZE[0], constants.texture.AO_TEXTURE_SIZE[1])

        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification(" - \U000025D9 Filling margin...")
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Filling margin...")
        common.texture.auto_fill_margin(target_texture)

        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification(" - \U0001f32b Blurring...")
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Blurring texture...")
        common.texture.blur_once(target_texture)

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Post-Processing Complete.")

    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Saving AO texture externally then deleting internally...")

    if not skip_pp:
        common.texture.save_image(target_texture, "BW", "8")
    else:
        common.texture.save_image(target_texture, "RGBA", "8")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("\U00002714 AO done", is_silent=False)
