import bpy

import common


def run():
    bpy.context.scene.display_settings.display_device = "sRGB"
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.sequencer_colorspace_settings.name = "Raw"

    bpy.context.area.type = "VIEW_3D"
    obj = bpy.context.view_layer.objects["Body"]
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode="OBJECT")
    common.blender.reset_ao()

    mat = obj.active_material
    common.blender.set_output_in_general_shader(obj, mat, "DefaultShader")
