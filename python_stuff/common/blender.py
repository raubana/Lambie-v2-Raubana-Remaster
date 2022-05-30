import bpy
import bpy_extras
import bpy_extras.mesh_utils

import constants
import common


def find_node_with_label(label, node_tree):
    for node in node_tree.nodes.values():
        if node.label == label:
            return node
    return None


def set_output_in_general_shader(obj, mat, target_node_label):
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.area.type = "NODE_EDITOR"

    general_shader_node = find_node_with_label("GeneralShader", mat.node_tree)
    if general_shader_node is None:
        raise Exception("Attempted to find a node labeled GeneralShader but didn't find one in the given node tree.")

    output_node = find_node_with_label("Output", general_shader_node.node_tree)
    if output_node is None:
        raise Exception("Attempted to find the node labeled Output within the general shader but didn't find it.")

    # We're gonna disconnect anything connected to the output first.
    for link in output_node.inputs[0].links:
        general_shader_node.node_tree.links.remove(link)

    # Next we find our target node.
    target_node = find_node_with_label(target_node_label, general_shader_node.node_tree)
    if target_node is None:
        raise Exception(
            "Attempted to find the node labeled '" + target_node_label + "' within the general shader but didn't find "
                                                                         "it.")

    # Connect the nodes!
    general_shader_node.node_tree.links.new(target_node.outputs[0], output_node.inputs[0])

    bpy.ops.node.select_all(action="DESELECT")
    bpy.context.area.type = "TEXT_EDITOR"
    bpy.ops.object.select_all(action="DESELECT")


def get_uv_islands(obj):
    islands = []

    poly_index_lists = bpy_extras.mesh_utils.mesh_linked_uv_islands(obj.data)

    for poly_index_list in poly_index_lists:
        island = []
        for poly_index in poly_index_list:
            island.append(obj.data.polygons[poly_index])
        islands.append(island)

    return islands


def load_ao():
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Loading AO...")

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Loading AO into memory...")
    bpy.ops.image.open(
        allow_path_tokens=True,
        filepath=constants.texture.TEXTURE_BAKED_FOLDER + constants.texture.TEXTURE_AO_NAME + constants.texture.TEXTURE_EXTENSION,
        relative_path=True
    )

    img = bpy.context.blend_data.images[constants.texture.TEXTURE_AO_NAME + constants.texture.TEXTURE_EXTENSION]
    # img.colorspace_settings.is_data = True

    # img.update()

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Done. Setting up general shader to use the AO texture...")

    obj = bpy.context.view_layer.objects["Body"]
    mat = obj.active_material

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.context.area.type = "NODE_EDITOR"

    general_shader_node = find_node_with_label("GeneralShader", mat.node_tree)
    if general_shader_node is None:
        raise Exception("Attempted to find a node labeled GeneralShader but didn't find one in the given node tree.")

    ao_input_node = find_node_with_label("AOInput", general_shader_node.node_tree)
    if ao_input_node is None:
        raise Exception("Attempted to find the node labeled AOInput within the general shader but didn't find it.")

    ao_texture_node = find_node_with_label("AOTextureNode", general_shader_node.node_tree)
    if ao_texture_node is None:
        raise Exception(
            "Attempted to find the node labeled AOTextureNode within the general shader but didn't find it.")

    # We're gonna disconnect anything connected to the ao input first.
    for link in ao_input_node.inputs[0].links:
        general_shader_node.node_tree.links.remove(link)

    # Now we connect the ao texture node to the ao input node.
    general_shader_node.node_tree.links.new(ao_texture_node.outputs[0], ao_input_node.inputs[0])

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Done. Loading the image into the texture node...")

    ao_texture_node.image = img

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Done. Cleaning up a little...")

    bpy.ops.node.select_all(action="DESELECT")
    bpy.context.area.type = "TEXT_EDITOR"
    bpy.ops.object.select_all(action="DESELECT")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def reset_ao():
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Resetting AO... ")

    if constants.texture.TEXTURE_AO_NAME + constants.texture.TEXTURE_EXTENSION in bpy.context.blend_data.images:
        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- AO texture found in memory. Deleting...")
        bpy.context.blend_data.images.remove(
            bpy.context.blend_data.images[constants.texture.TEXTURE_AO_NAME + constants.texture.TEXTURE_EXTENSION])

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Resetting the general shader...")

    obj = bpy.context.view_layer.objects["Body"]
    mat = obj.active_material

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.context.area.type = "NODE_EDITOR"

    general_shader_node = find_node_with_label("GeneralShader", mat.node_tree)
    if general_shader_node is None:
        raise Exception("Attempted to find a node labeled GeneralShader but didn't find one in the given node tree.")

    ao_input_node = find_node_with_label("AOInput", general_shader_node.node_tree)
    if ao_input_node is None:
        raise Exception("Attempted to find the node labeled AOInput within the general shader but didn't find it.")

    ao_texture_node = find_node_with_label("AOTextureNode", general_shader_node.node_tree)
    if ao_texture_node is None:
        raise Exception(
            "Attempted to find the node labeled AOTextureNode within the general shader but didn't find it.")

    input_node = find_node_with_label("Input", general_shader_node.node_tree)
    if input_node is None:
        raise Exception("Attempted to find the node labeled Input within the general shader but didn't find it.")

    # We're gonna disconnect anything connected to the ao input first.
    for link in ao_input_node.inputs[0].links:
        general_shader_node.node_tree.links.remove(link)

    # Now we connect the input to the ao input node.
    general_shader_node.node_tree.links.new(input_node.outputs[0], ao_input_node.inputs[0])

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Done. Cleaning up a little...")

    bpy.ops.node.select_all(action="DESELECT")
    bpy.context.area.type = "TEXT_EDITOR"
    bpy.ops.object.select_all(action="DESELECT")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")


def find_layer_collection_of_collection(target_collection, current_layer_collection):
    #https://blenderartists.org/t/make-latest-created-collection-active/1350762/5?u=raubana
    for layer_collection in current_layer_collection.children:
        if layer_collection.collection == target_collection:
            return layer_collection
    return None