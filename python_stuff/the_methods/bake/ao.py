import math

import bpy

import common
import constants

import notifications


def run(skip_pp=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Baking All Ambient Occlusion   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("\U0001f4a1 Baking AO", is_silent=False)

    if bpy.context.scene.render.engine != "CYCLES":
        raise Exception("Can't bake AO in this render engine. Must be set to Cycles.")

    num_samples = constants.bake.AO_CYCLES_SAMPLES
    if constants.bake.AO_CYCLES_BADAA:
        num_samples = int(math.ceil(num_samples/constants.bake.AO_CYCLES_BADAA_SCALE))

    bpy.context.scene.cycles.samples = num_samples
    bpy.context.scene.cycles.tile_size = constants.bake.CYCLES_TILESIZE

    bpy.context.scene.cycles.diffuse_bounces = constants.bake.AO_CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.glossy_bounces = 0
    bpy.context.scene.cycles.transmission_bounces = 0
    bpy.context.scene.cycles.volume_bounces = 0
    bpy.context.scene.cycles.transparent_max_bounces = 0
    bpy.context.scene.cycles.max_bounces = constants.bake.AO_CYCLES_MAXBOUNCES

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Creating AO texture '" + constants.texture.TEXTURE_AO_NAME + "'...")
    size = constants.texture.AO_TEXTURE_SIZE
    if constants.bake.AO_CYCLES_BADAA:
        size = (constants.texture.AO_TEXTURE_SIZE[0] * constants.bake.AO_CYCLES_BADAA_SCALE, constants.texture.AO_TEXTURE_SIZE[1] * constants.bake.AO_CYCLES_BADAA_SCALE)
    ao_texture = common.texture.make_blank_image(constants.texture.TEXTURE_AO_NAME + constants.texture.TEXTURE_EXTENSION, size, fill_color=(0.5,0.5,0.5,0.0))
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - AO texture created. Prepping to bake... ")

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Prepping armature '" + constants.blender.ARMATURE_NAME + "'")
    if not constants.blender.ARMATURE_NAME in bpy.context.view_layer.objects:
        raise Exception(
            "Attempted to prep armature '" + constants.blender.ARMATURE_NAME + "' before batch baking AO but couldn't find it in this context.")
    armature = bpy.context.view_layer.objects[constants.blender.ARMATURE_NAME]
    armature.hide_set(False)
    armature.hide_viewport = False

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    for object_name in constants.blender.EVERYTHING:
        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Prepping object '" + object_name + "'...")
        if not object_name in bpy.context.view_layer.objects:
            raise Exception(
                "Attempted to prep object '" + object_name + "' before batch baking AO but couldn't find it in this context.")
        obj = bpy.context.view_layer.objects[object_name]
        obj.hide_set(False)
        obj.hide_render = True
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shape_key_clear()
        bpy.ops.object.select_all(action="DESELECT")
        if not constants.blender.UV_NAME in obj.data.uv_layers:
            raise Exception("Object '" + object_name + "' lacks the expected UV map named '" + constants.blender.UV_NAME + "'")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - All prepped. Commencing AO baking...")
    for target_object_name in constants.blender.EVERYTHING:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
            "- \U0001f526 Baking AO for object '" + target_object_name)

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Object '" + target_object_name + "'")

        obj = bpy.context.view_layer.objects[target_object_name]

        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Generating settings...")
        settings = dict(constants.bake.AO_DEFAULTSETTINGS)

        if target_object_name in constants.bake.AO_SETTINGS:
            for custom_setting_key in constants.bake.AO_SETTINGS[target_object_name]:
                if custom_setting_key == "enabled" or custom_setting_key == "disabled":
                    if custom_setting_key in settings:
                        settings[custom_setting_key] = settings[custom_setting_key] + constants.bake.AO_SETTINGS[target_object_name][
                            custom_setting_key]
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
        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Settings generated.")

        if "skip" in settings and settings["skip"] is True:
            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Object marked to be skipped. Skipping.")
        else:
            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Prepping target object's material...")

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
            tex_node.image = ao_texture

            mat.node_tree.links.new(uvmap_node.outputs[0], tex_node.inputs[0])

            bpy.ops.node.select_all(action="DESELECT")
            tex_node.select = True
            mat.node_tree.nodes.active = tex_node

            bpy.context.area.type = "TEXT_EDITOR"

            bpy.ops.object.select_all(action="DESELECT")

            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Material prepped. Applying settings...")

            # First we set up this object, because... I mean, duh.
            obj.hide_set(False)
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
                    if "disabled" in settings and key in settings["disabled"]:
                        pass
                    else:
                        if key not in bpy.context.view_layer.objects:
                            raise Exception(
                                "Attempted to enable object '" + key + "' before baking AO for object '" + target_object_name + "' but couldn't find it in this context.")
                        obj2 = bpy.context.view_layer.objects[key]
                        obj2.hide_set(False)
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
            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Settings applied. Baking AO...")

            margin = constants.bake.AO_TEXTURE_BAKINGMARGIN
            if margin == -1:
                margin = min(constants.texture.AO_TEXTURE_SIZE) * constants.uv.UV_MARGIN
            if constants.bake.AO_CYCLES_BADAA:
                margin *= constants.bake.AO_CYCLES_BADAA_SCALE
            margin = int(math.floor(margin))

            bpy.ops.object.bake(
                type="AO",
                pass_filter={"DIFFUSE"},
                target="IMAGE_TEXTURES",
                save_mode="INTERNAL",
                margin=margin,
                margin_type=constants.bake.AO_TEXTURE_BAKINGMARGIN_TYPE,
                uv_layer=constants.blender.UV_NAME
            )

            if constants.bake.TEXTURE_SAVEASYOUBAKE:
                common.texture.save_image(ao_texture, "RGBA", "16", delete_from_memory=False)

            # Gotta reset now that baking is finished for this object.
            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Done baking AO. Resetting...")

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
                    if "disabled" in settings and key in settings["disabled"]:
                        pass
                    else:
                        obj2 = bpy.context.view_layer.objects[key]
                        obj2.hide_set(False)
                        obj2.hide_render = True

            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.context.area.type = "NODE_EDITOR"

            mat.node_tree.nodes.remove(uvmap_node)
            mat.node_tree.nodes.remove(tex_node)

            bpy.context.area.type = "TEXT_EDITOR"

            bpy.ops.object.select_all(action="DESELECT")

            obj.hide_set(False)
            obj.hide_render = True

            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Reset.")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - AO baking done for all objects.")

    if not skip_pp:
        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification("\U0001f51c Finished baking AO, finishing up")

        if constants.bake.AO_CYCLES_BADAA:
            if notifications.constants.ENABLED:
                notifications.constants.HANDLER.add_notification(" - \U000025F0 Resizing (Bad AA)...")
            if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resizing (Bad AA)...")
            ao_texture.scale(constants.texture.AO_TEXTURE_SIZE[0], constants.texture.AO_TEXTURE_SIZE[1])

        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification(" - \U000025D9 Filling margin...")
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Filling margin...")
        common.texture.auto_fill_margin(ao_texture)

        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification(" - \U0001f32b Blurring...")
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Blurring texture...")
        common.texture.blur_once(ao_texture)

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Post-Processing Complete.")

    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Saving AO texture externally then deleting internally...")

    if not skip_pp:
        common.texture.save_image(ao_texture, "BW", "8")
    else:
        common.texture.save_image(ao_texture, "RGBA", "8")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("\U00002714 AO done", is_silent=False)
