import bpy

import common
import constants


def run():
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    bpy.context.scene.display_settings.display_device = "sRGB"
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.sequencer_colorspace_settings.name = "Raw"

    # Make everything visible.
    for obj_name in constants.blender.EVERYTHING:
        obj = bpy.context.view_layer.objects[obj_name]

        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False

    # Reset armature.
    if not constants.blender.ARMATURE_NAME in bpy.context.view_layer.objects:
        raise Exception("Attempted to reset armature '" + constants.blender.ARMATURE_NAME + "' but couldn't find it in this context.")

    armature = bpy.context.view_layer.objects[constants.blender.ARMATURE_NAME]

    armature.hide_set(False)
    armature.hide_viewport = False
    armature.hide_render = False

    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action='SELECT')

    bpy.ops.pose.transforms_clear()

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    # Reset material nodes.
    obj = bpy.context.view_layer.objects["Body"]
    bpy.context.view_layer.objects.active = obj

    common.blender.reset_ao()

    mat = obj.active_material
    common.blender.set_output_in_general_shader(obj, mat, "DefaultShader")

    # Reset everything else.
    for obj_name in constants.blender.EVERYTHING:
        obj = bpy.context.view_layer.objects[obj_name]

        bpy.ops.object.select_all(action="DESELECT")

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.shape_key_clear()

        obj.active_shape_key_index = 0
