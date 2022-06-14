import os
import math
import PIL.Image
import ctypes

import bpy
import mathutils

import common
import constants

import notifications


def generic(image_name, image_size, print_label, target_node_label, bake_type="EMIT", color_space="sRGB",
                 fill_color=(0.5, 0.5, 0.5, 0.0), skip_pp=False, attempt_resume=None):

    common.general.safe_print("\n")
    common.general.safe_print(" ===   Baking "+print_label+"   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U0001f4f8 Baking generic '" + print_label + "'", is_silent=False)

    attempt_resume_order = (
        "baking",
        "stitching",
        "before pp",
        "resize",
        "margin",
        "after pp"
    )

    if attempt_resume is not None:
        if type(attempt_resume) in (list, tuple):
            if len(attempt_resume) == 0:
                raise Exception("Can't resume anywhere without specifying where to resume at.")
        else:
            raise Exception("Keyword 'attempt_resume' expects a list or a tuple.")

    if bpy.context.scene.render.engine != "CYCLES":
        raise Exception("Can't bake in this render engine. Must be set to Cycles.")

    num_samples = constants.bake.CYCLES_SAMPLES
    if constants.bake.CYCLES_BAD_MSAA:
        num_samples = int(math.ceil(num_samples / (constants.bake.CYCLES_BAD_MSAA_SCALE**2)))

    bpy.context.scene.cycles.samples = num_samples

    bpy.context.scene.cycles.diffuse_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.glossy_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.transmission_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.volume_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.transparent_max_bounces = constants.bake.CYCLES_MAXBOUNCES
    bpy.context.scene.cycles.max_bounces = constants.bake.CYCLES_MAXBOUNCES

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Creating texture '" + image_name + "'...")
    size = image_size
    if constants.bake.CYCLES_BAD_MSAA:
        size = (image_size[0] * constants.bake.CYCLES_BAD_MSAA_SCALE, image_size[1] * constants.bake.CYCLES_BAD_MSAA_SCALE)

    num_tiles = [1,1]
    if constants.bake.CYCLES_STITCHING:
        num_tiles = [
            int(math.ceil(size[0]/constants.bake.CYCLES_STITCHING_TILESIZE)),
            int(math.ceil(size[1]/constants.bake.CYCLES_STITCHING_TILESIZE))
        ]

    margin = constants.bake.TEXTURE_BAKINGMARGIN
    if margin == -1:
        if constants.bake.CYCLES_STITCHING:
            margin = constants.bake.CYCLES_STITCHING_TILESIZE
        else:
            margin = min(constants.texture.TEXTURE_SIZE)
        margin *= constants.uv.UV_MARGIN
    if constants.bake.CYCLES_BAD_MSAA:
        margin *= constants.bake.CYCLES_BAD_MSAA_SCALE
    margin = int(math.floor(margin)) - 1
    if margin < 0: margin = 0

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - MARGIN:", margin)

    tile_texture = None
    for tile_y in range(num_tiles[1]):
        if attempt_resume is not None:
            if attempt_resume[0] == "baking" and tile_y == attempt_resume[2]:
                if constants.other.VERBOSE_LEVEL >= 1:
                    common.general.safe_print(" - PARTIALLY RESUMED AT TILE ROW", tile_y)
            else:
                if constants.other.VERBOSE_LEVEL >= 1:
                    common.general.safe_print(" - SKIPPING TILE ROW", tile_y)
                continue

        for tile_x in range(num_tiles[0]):
            if attempt_resume is not None:
                if attempt_resume[0] == "baking" and tile_x == attempt_resume[1]:
                    if len(attempt_resume) <= 3:
                        attempt_resume = None

                        if constants.other.VERBOSE_LEVEL >= 1:
                            common.general.safe_print(" - RESUMED AT TILE", tile_x, tile_y)
                    else:
                        if constants.other.VERBOSE_LEVEL >= 1:
                            common.general.safe_print(" - PARTIALLY RESUMED AT TILE", tile_x, tile_y)
                else:
                    if constants.other.VERBOSE_LEVEL >= 1:
                        common.general.safe_print(" - SKIPPING TILE COLUMN", tile_x)
                    continue

            if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
                " - \U000025A6 TILE ["+str(tile_x)+"/"+str(num_tiles[0])+", "+str(tile_y)+"/"+str(num_tiles[1])+"]")

            if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print("\n -- TILE:", tile_x, ",", tile_y)

            tile_uvmap_name = constants.blender.UV_NAME
            tile_name = image_name
            tile_dims = list(size)
            if constants.bake.CYCLES_STITCHING:
                tile_uvmap_name = "TEMP_UVMap"

                tile_name = "TEMP_tile_" + str(tile_x) + "_" + str(tile_y) + constants.texture.TEXTURE_EXTENSION

                tile_dims = [constants.bake.CYCLES_STITCHING_TILESIZE, constants.bake.CYCLES_STITCHING_TILESIZE]

                if tile_x == num_tiles[0] - 1:
                    xmod = size[0]%constants.bake.CYCLES_STITCHING_TILESIZE
                    if xmod > 0: tile_dims[0] = xmod

                if tile_y == num_tiles[1] - 1:
                    ymod = size[1]%constants.bake.CYCLES_STITCHING_TILESIZE
                    if ymod > 0: tile_dims[1] = ymod

            if tile_texture is None:
                tile_texture = common.texture.make_blank_image(
                    tile_name, tile_dims, color_space=color_space, fill_color=fill_color
                )

            if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Texture created. Prepping to bake... ")

            # The UV system uses the typical coordinate system most people know, where +x is right and +y is UP.
            # In other words, the origin is in the BOTTOM-left.

            # However, PIL uses the computer standard, where +x is right and +y is DOWN.
            # In other words, the origin is in the TOP-left.

            # For the sake of consistency, I'm going to force PIL to act like it uses the typical coordinate system
            # standard, so stitching will be much easier.

            m = mathutils.Matrix.Translation((
                -(tile_x*constants.bake.CYCLES_STITCHING_TILESIZE)/size[0],
                -(tile_y*constants.bake.CYCLES_STITCHING_TILESIZE)/size[1],
                0.0
            ))

            m = mathutils.Matrix.Scale(
                size[0]/tile_dims[0],
                4, mathutils.Vector((1, 0, 0))) @ m

            m = mathutils.Matrix.Scale(
                size[1]/tile_dims[1],
                4, mathutils.Vector((0, 1, 0))) @ m

            obj_has_uv_in_bounds = {}

            for object_name in constants.blender.EVERYTHING:
                obj_has_uv_in_bounds[object_name] = True

            for object_name in constants.blender.EVERYTHING:
                if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Prepping object '" + object_name + "'...")
                if object_name not in bpy.context.view_layer.objects:
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

                if constants.blender.UV_NAME not in obj.data.uv_layers:
                    raise Exception("Object '" + object_name + "' lacks the expected UV map named '" + constants.blender.UV_NAME + "'")
                else:
                    original_uvmap = obj.data.uv_layers[constants.blender.UV_NAME]

                    obj.data.uv_layers.active = original_uvmap

                    if constants.bake.CYCLES_STITCHING:
                        obj_has_uv_in_bounds[object_name] = False

                        if "TEMP_UVMap" in obj.data.uv_layers:
                            obj.data.uv_layers.remove( obj.data.uv_layers["TEMP_UVMap"] )

                        temp_uvmap = obj.data.uv_layers.new(name="TEMP_UVMap", do_init=True)

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

                                for loop_index in range(loop_start_index + 1, loop_start_index + loop_total):
                                    uv = temp_uvmap.data[loop_index].uv

                                    min_x = min(min_x, uv.x)
                                    min_y = min(min_y, uv.y)
                                    max_x = max(max_x, uv.x)
                                    max_y = max(max_y, uv.y)

                                min_x = min_x * tile_dims[0] - margin
                                min_y = min_y * tile_dims[1] - margin
                                max_x = max_x * tile_dims[0] + margin
                                max_y = max_y * tile_dims[1] + margin

                                # https://www.geeksforgeeks.org/find-two-rectangles-overlap/
                                if not (max_x < 0 or min_x > tile_dims[0] or min_y < 0 or max_y > tile_dims[1]):
                                    obj_has_uv_in_bounds[object_name] = True
                                    break

                            if obj_has_uv_in_bounds[object_name]:
                                break

                            obj.data.uv_layers.active = original_uvmap

            if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- All prepped. Commencing baking...")
            for target_object_name in constants.blender.EVERYTHING:
                if attempt_resume is not None:
                    if attempt_resume[0] == "baking" and target_object_name == attempt_resume[3]:
                        attempt_resume = None

                        if constants.other.VERBOSE_LEVEL >= 1:
                            common.general.safe_print(" - RESUMED AT OBJECT", target_object_name)
                    else:
                        if constants.other.VERBOSE_LEVEL >= 1:
                            common.general.safe_print(" - SKIPPING BAKING OBJECT", target_object_name)
                        continue

                if obj_has_uv_in_bounds[target_object_name] is not True:
                    if constants.other.VERBOSE_LEVEL >= 3:
                        common.general.safe_print(" --- Object '" + target_object_name + "' not in tile...")
                    continue # We skip objects that won't show up on the tile.

                #if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
                #    " -- \U0001f39e Baking object '" + target_object_name)

                if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Object '" + target_object_name + "'")

                obj = bpy.context.view_layer.objects[target_object_name]

                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Prepping target object's material...")

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

                uvmap_node.uv_map = tile_uvmap_name
                tex_node.image = tile_texture

                mat.node_tree.links.new(uvmap_node.outputs[0], tex_node.inputs[0])

                bpy.ops.node.select_all(action="DESELECT")
                tex_node.select = True
                mat.node_tree.nodes.active = tex_node

                bpy.context.area.type = "TEXT_EDITOR"

                bpy.ops.object.select_all(action="DESELECT")

                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Material prepped.")

                # Deselecting everything and selecting our target object.
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

                # Now we bake!
                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Baking...")

                bpy.ops.object.bake(
                    type=bake_type,
                    target="IMAGE_TEXTURES",
                    save_mode="INTERNAL",
                    margin=margin,
                    margin_type=constants.bake.TEXTURE_BAKINGMARGIN_TYPE,
                    use_selected_to_active=False,
                    use_clear=False,
                    uv_layer=tile_uvmap_name
                )

                common.texture.save_image(
                    bpy.context.blend_data.images[tile_name],
                    "RGBA",
                    "16",
                    delete_from_memory = False
                )

                if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Done baking this object.")

                bpy.ops.object.select_all(action="DESELECT")
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

                bpy.context.area.type = "NODE_EDITOR"

                mat.node_tree.nodes.remove(uvmap_node)
                mat.node_tree.nodes.remove(tex_node)

                bpy.context.area.type = "TEXT_EDITOR"

                bpy.ops.object.select_all(action="DESELECT")

                if constants.bake.CYCLES_STITCHING:
                    obj.data.uv_layers.remove(obj.data.uv_layers["TEMP_UVMap"])

            if constants.bake.CYCLES_STITCHING:
                bpy.context.blend_data.images.remove(tile_texture)
                tile_texture = None

    if tile_texture is not None:
        bpy.context.blend_data.images.remove(tile_texture)
        del tile_texture

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print("\n - Baking done for all objects.")

    skip_stitching = False
    if attempt_resume is not None:
        if attempt_resume[0] == "stitching":
            attempt_resume = None

            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - RESUMING BEFORE STITCHING")
        else:
            skip_stitching = True

            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - SKIPPING STITCHING")

    if constants.bake.CYCLES_STITCHING and not skip_stitching:
        #https://stackoverflow.com/questions/10657383/stitching-photos-together

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Stitching tiles...")

        new_fill_color = []
        for channel in fill_color:
            new_fill_color.append( int(channel) )
        new_fill_color[-1] = 0
        new_fill_color = tuple(new_fill_color)

        final_image = PIL.Image.new("RGBA", size, new_fill_color)

        last_tile_dims = [
            int(size[0] % constants.bake.CYCLES_STITCHING_TILESIZE),
            int(size[1] % constants.bake.CYCLES_STITCHING_TILESIZE)
        ]

        if last_tile_dims[0] == 0: last_tile_dims[0] = constants.bake.CYCLES_STITCHING_TILESIZE
        if last_tile_dims[1] == 0: last_tile_dims[1] = constants.bake.CYCLES_STITCHING_TILESIZE

        for tile_y in range(num_tiles[1]):
            for tile_x in range(num_tiles[0]):
                tile_name = "TEMP_tile_" + str(tile_x) + "_" + str(tile_y) + constants.texture.TEXTURE_EXTENSION
                fp = common.general.clean_filepath( constants.texture.TEXTURE_BAKED_FOLDER + tile_name )

                if os.path.isfile(fp):
                    tile = PIL.Image.open(fp)

                    pos = [
                        tile_x * constants.bake.CYCLES_STITCHING_TILESIZE,
                        size[1] - (tile_y * constants.bake.CYCLES_STITCHING_TILESIZE) - last_tile_dims[1]
                    ]

                    final_image.paste(tile, tuple(pos))

                    del tile
                else:
                    if constants.other.VERBOSE_LEVEL >= 2:
                        common.general.safe_print(" -- could not find file: " + tile_name)

        #if constants.bake.CYCLES_BAD_MSAA:
        #    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resizing...")
        #    final_image = final_image.resize(constants.texture.TEXTURE_SIZE, resample=PIL.Image.Resampling.LANCZOS)

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Saving final image...")
        final_image.save( common.general.clean_filepath(
            constants.texture.TEXTURE_BAKED_FOLDER + image_name
        ))

        del final_image

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Cleaning up tile images...")

        for tile_y in range(num_tiles[1]):
            for tile_x in range(num_tiles[0]):
                tile_name = "TEMP_tile_" + str(tile_x) + "_" + str(tile_y) + constants.texture.TEXTURE_EXTENSION

                common.general.safely_delete_file(constants.texture.TEXTURE_BAKED_FOLDER + tile_name)

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Loading texture back into memory...")

    bpy.ops.image.open(
        allow_path_tokens=True,
        filepath= common.general.clean_filepath(
            constants.texture.TEXTURE_BAKED_FOLDER + image_name
        ),
        relative_path=True
    )

    target_texture = bpy.context.blend_data.images[image_name]

    if attempt_resume is not None:
        if attempt_resume[0] == "before pp":
            attempt_resume = None

            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - RESUMING AT POST-PROCESSING")

        elif attempt_resume[0] not in attempt_resume_order or \
            (attempt_resume_order.index(attempt_resume[0]) >= attempt_resume_order.index("after pp")):
            skip_pp = True

            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - SKIPPING POST-PROCESSING")
        else:
            if constants.other.VERBOSE_LEVEL >= 1:
                common.general.safe_print(" - PARTIALLY RESUMING AT POST-PROCESSING")

    if not skip_pp:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
            "\U0001f51c Baking done for generic '" + print_label + "', finishing up")

        skip_resize = False
        if attempt_resume is not None:
            if attempt_resume[0] not in attempt_resume_order or \
                    (attempt_resume_order.index(attempt_resume[0]) > attempt_resume_order.index("resize")):
                skip_resize = True

                if constants.other.VERBOSE_LEVEL >= 1:
                    common.general.safe_print(" - SKIPPING RESIZE")
            else:
                attempt_resume = None

                if constants.other.VERBOSE_LEVEL >= 1:
                    common.general.safe_print(" - RESUMING AT RESIZE")

        if constants.bake.CYCLES_BAD_MSAA and not skip_resize:
            if notifications.constants.ENABLED:
                notifications.constants.HANDLER.add_notification(" - \U000025F0 Resizing (Bad MSAA)...")
            if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resizing (Bad MSAA)...")
            target_texture.scale(constants.texture.TEXTURE_SIZE[0], constants.texture.TEXTURE_SIZE[1])

        skip_margin = False
        if attempt_resume is not None:
            if attempt_resume[0] not in attempt_resume_order or \
                    (attempt_resume_order.index(attempt_resume[0]) > attempt_resume_order.index("margin")):
                skip_margin = True

                if constants.other.VERBOSE_LEVEL >= 1:
                    common.general.safe_print(" - SKIPPING FILLING MARGIN")
            else:
                attempt_resume = None

                if constants.other.VERBOSE_LEVEL >= 1:
                    common.general.safe_print(" - RESUMING AT FILLING MARGIN")

        if not skip_margin:
            if notifications.constants.ENABLED:
                notifications.constants.HANDLER.add_notification(" - \U000025D9 Filling margin...")
            if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Filling margin...")
            common.texture.auto_fill_margin(target_texture)

        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Post-Processing Complete.")

    if attempt_resume is not None and attempt_resume[0] == "after pp":
        attempt_resume = None
        if constants.other.VERBOSE_LEVEL >= 1:
            common.general.safe_print(" - RESUMING AFTER POST-PROCESSING")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U00002714 Generic '" + print_label + "' complete.", is_silent=False)

    return target_texture


def albedo(skip_pp=False, attempt_resume=None):
    img = generic(
        constants.texture.TEXTURE_ALBEDO_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "Albedo", "AlbedoAO", skip_pp=skip_pp, attempt_resume=attempt_resume
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def specular(skip_pp=False, attempt_resume=None):
    img = generic(
        constants.texture.TEXTURE_SPECULAR_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "Specular", "SpecularAO", skip_pp=skip_pp, attempt_resume=attempt_resume
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def smoothness(skip_pp=False, attempt_resume=None):
    img = generic(
        constants.texture.TEXTURE_SMOOTHNESS_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "Smoothness", "SmoothnessAO", skip_pp=skip_pp, attempt_resume=attempt_resume
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "BW", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def emissions(skip_pp=False, attempt_resume=None):
    img = generic(
        constants.texture.TEXTURE_EMISSIONS_NAME + constants.texture.TEXTURE_EXTENSION, constants.texture.TEXTURE_SIZE,
        "Emissions", "EmissionsAO", fill_color=(0.0, 0.0, 0.0, 0.0), skip_pp=skip_pp, attempt_resume=attempt_resume
    )
    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "8")
    else:
        common.texture.save_image(img, "RGBA", "8")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def normals(skip_pp=False, attempt_resume=None):
    img = generic(
        constants.texture.TEXTURE_NORMALS_NAME + constants.texture.TEXTURE_EXTENSION,
        constants.texture.TEXTURE_SIZE, "Normals", "DiffuseShader", bake_type="NORMAL", color_space="Non-Color",
        fill_color=(0.5, 0.5, 1.0, 0.0), skip_pp=skip_pp, attempt_resume=attempt_resume
    )

    """
    if constants.bake.CYCLES_STITCHING:
        if constants.other.VERBOSE_LEVEL >= 1:
            common.general.safe_print(" - Attempting to kind of 'repair' the damage caused by PIL...")

            half_float = 1/2
            half_float_with_error = ((1/3 + 1/2) + (2**64)) - (2**64) - (1/3)

            holder = common.general.Holder(img.pixels)

            for y in range( img.height ):
                for x in range( img.width ):
                    pixel_index = common.texture.coords_to_index((x,y), img.size, img.channels)
                    pixel = holder.held[pixel_index:pixel_index+img.channels]
                    new_pixel = []
                    for channel in pixel:
                        if channel <= half_float:
                            new_pixel.append( half_float * (channel / half_float_with_error) )
                        else:
                            new_pixel.append( half_float * ((channel-half_float_with_error) / (1-half_float_with_error)) )

                    holder.held[pixel_index:pixel_index+img.channels] = new_pixel

            img.pixels = holder.held
            img.update()
    """

    if constants.other.VERBOSE_LEVEL >= 1:
        common.general.safe_print(" - Done. Saving texture externally then deleting internally...")
    if not skip_pp:
        common.texture.save_image(img, "RGB", "16")
    else:
        common.texture.save_image(img, "RGBA", "16")
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


