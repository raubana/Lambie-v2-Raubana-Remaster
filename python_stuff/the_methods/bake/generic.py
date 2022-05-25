import math

import bpy

import common
import constants

import notifications


def generic(image_name, image_size, target_node_label, bake_type="EMIT", color_space="sRGB",
                 fill_color=(0.5, 0.5, 0.5, 0.0), skip_pp=False):
    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U0001f4f8 Baking generic '" + target_node_label, is_silent=False)

    if bpy.context.scene.render.engine != "CYCLES":
        raise Exception("Can't bake in this render engine. Must be set to Cycles.")

    num_samples = constants.bake.CYCLES_SAMPLES
    if constants.bake.CYCLES_BADAA:
        num_samples = int(math.ceil(num_samples / constants.bake.CYCLES_BADAA_SCALE))

    bpy.context.scene.cycles.samples = num_samples
    bpy.context.scene.cycles.tile_size = constants.bake.CYCLES_TILESIZE

    bpy.context.scene.cycles.diffuse_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.glossy_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.transmission_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.volume_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.transparent_max_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.max_bounces = constants.bake.CYCLES_MAXBOUNCES

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Creating texture '" + image_name + "'...")
    size = image_size
    if constants.bake.CYCLES_BADAA:
        size = (image_size[0] * constants.bake.CYCLES_BADAA_SCALE, image_size[1] * constants.bake.CYCLES_BADAA_SCALE)
    target_texture = common.texture.make_blank_image(image_name, size, color_space=color_space, fill_color=fill_color)
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Texture created. Prepping to bake... ")

    for object_name in constants.blender.EVERYTHING:
        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Prepping object '" + object_name + "'...")
        if not object_name in bpy.context.view_layer.objects:
            raise Exception(
                "Attempted to prep object '" + object_name + "' before batch baking but couldn't find it in this context.")
        obj = bpy.context.view_layer.objects[object_name]
        obj.hide_set(False)
        obj.hide_render = False
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shape_key_clear()
        bpy.ops.object.select_all(action="DESELECT")
        if not constants.uv.UV_NAME in obj.data.uv_layers:
            raise Exception("Object '" + object_name + "' lacks the expected UV map named '" + constants.uv.UV_NAME + "'")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - All prepped. Commencing baking...")
    for target_object_name in constants.blender.EVERYTHING:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
            "- \U0001f39e Baking object '" + target_object_name)

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Object '" + target_object_name + "'")

        obj = bpy.context.view_layer.objects[target_object_name]

        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Prepping target object's material...")

        # https://blender.stackexchange.com/questions/23436/control-cycles-eevee-material-nodes-and-material-properties-using-python/23446
        mat = obj.active_material
        if mat is None:
            raise Exception("Object '" + target_object_name + "' has no active material.")

        common.blender.set_output_in_general_shader(obj, mat, target_node_label)

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.context.area.type = "NODE_EDITOR"

        uvmap_node = mat.node_tree.nodes.new(type='ShaderNodeUVMap')
        tex_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')

        uvmap_node.uv_map = constants.uv.UV_NAME
        tex_node.image = target_texture

        mat.node_tree.links.new(uvmap_node.outputs[0], tex_node.inputs[0])

        bpy.ops.node.select_all(action="DESELECT")
        tex_node.select = True
        mat.node_tree.nodes.active = tex_node

        bpy.context.area.type = "TEXT_EDITOR"

        bpy.ops.object.select_all(action="DESELECT")

        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Material prepped.")

        # Deselecting everything and selecting our target object.
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Now we bake!
        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Baking...")

        margin = constants.bake.TEXTURE_BAKINGMARGIN
        if margin == -1:
            margin = min(constants.texture.TEXTURE_SIZE) * constants.uv.UV_MARGIN
        if constants.bake.CYCLES_BADAA:
            margin *= constants.bake.CYCLES_BADAA_SCALE
        margin = int(math.floor(margin))

        bpy.ops.object.bake(
            type=bake_type,
            target="IMAGE_TEXTURES",
            save_mode="INTERNAL",
            margin=margin,
            margin_type=constants.bake.TEXTURE_BAKINGMARGIN_TYPE,
            uv_layer=constants.uv.UV_NAME
        )

        if constants.bake.TEXTURE_SAVEASYOUBAKE:
            common.texture.save_image(
                bpy.context.blend_data.images[image_name],
                "RGBA",
                "16",
                delete_from_memory=False
            )

        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Done baking this object.")

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.context.area.type = "NODE_EDITOR"

        mat.node_tree.nodes.remove(uvmap_node)
        mat.node_tree.nodes.remove(tex_node)

        bpy.context.area.type = "TEXT_EDITOR"

        bpy.ops.object.select_all(action="DESELECT")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Baking done for all objects.")

    if not skip_pp:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
            "\U0001f51c Baking done for generic '" + target_node_label + "', finishing up")

        if constants.bake.CYCLES_BADAA:
            if notifications.constants.ENABLED:
                notifications.constants.HANDLER.add_notification(" - \U000025F0 Resizing (Bad AA)...")
            if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resizing (Bad AA)...")
            target_texture.scale(image_size[0], image_size[1])

        if notifications.constants.ENABLED:
            notifications.constants.HANDLER.add_notification(" - \U000025D9 Filling margin...")
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Filling margin...")
        common.texture.auto_fill_margin(target_texture)

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Post-Processing Complete.")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U00002714 Done with generic '" + target_node_label, is_silent=False)

    return target_texture


def albedo(skip_pp=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Baking Albedo   === ")
    img = generic(
        constants.texture.TEXTURE_ALBEDO_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "AlbedoAO", skip_pp=skip_pp
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def specular(skip_pp=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Baking Specular   === ")
    img = generic(
        constants.texture.TEXTURE_SPECULAR_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "SpecularAO", skip_pp=skip_pp
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def smoothness(skip_pp=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Baking Smoothness   === ")
    img = generic(
        constants.texture.TEXTURE_SMOOTHNESS_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "SmoothnessAO", skip_pp=skip_pp
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "BW", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def emissions(skip_pp=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Baking Emissions   === ")
    img = generic(
        constants.texture.TEXTURE_EMISSIONS_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "EmissionsAO", fill_color=(0.0, 0.0, 0.0, 0.0), skip_pp=skip_pp)
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def normals(skip_pp=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Baking Normals   === ")
    img = generic(
        constants.texture.TEXTURE_NORMALS_NAME + constants.texture.TEXTURE_EXTENSION,
        constants.texture.TEXTURE_SIZE, "DiffuseShader", bake_type="NORMAL", color_space="Non-Color",
        fill_color=(0.5, 0.5, 1.0, 0.0), skip_pp=skip_pp
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")
