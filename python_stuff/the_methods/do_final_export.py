import random, time

import bpy

import common
import constants

import notifications


def run( skip_warning=False, merge_meshes=True ):
    common.general.safe_print("")
    common.general.safe_print(" ===   Exporting FBX   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "- \U0001f4e6 Exporting FBX...", is_silent=False)

    if not skip_warning:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
            "- \U000026a0 WAITING FOR USER INPUT", is_silent=False)

        # First we warn the user of what's about to happen.
        common.general.safe_print("\n\n\nNOTICE TO USER:")
        common.general.safe_print("The following is about to happen:")
        common.general.safe_print("\n1. The entire Blender file will be saved as a new file with '_TEMP' at the end.")
        common.general.safe_print("\t\tIf it already exists, IT WILL BE OVERWRITTEN!")
        common.general.safe_print("\t\tANY UNSAVED CHANGES WILL NOT BE IN THE ORIGINAL FILE!")
        common.general.safe_print("\n2. The model in the copy will be modified in preparation for Unity/VRChat.")
        common.general.safe_print("\n3. The temporary Blender file will be saved.")
        common.general.safe_print("\n4. The model will be exported as '"+constants.blender.EXPORT_NAME+".fbx' locally.")
        common.general.safe_print("\t\tAgain, if it already exists, IT MAY BE OVERWRITTEN!")
        common.general.safe_print("\n5. The original file will be reopened.")
        common.general.safe_print("\t\tThe copy will NOT be deleted by this script.")
        common.general.safe_print("\n\nIf you understand and are ready to execute, please solve the following:\n")

        a = random.randint(-5,5)
        b = random.randint(-5,5)

        op = random.choice(('+','-','*'))

        solution = None
        if op == '+': solution = a+b
        elif op == '-': solution = a-b
        elif op == '*': solution = a*b
        else: raise Exception("That shouldn't have happened.")

        constants.other.PRINT_LOCK.acquire()
        user_input = input("\t"+str(a)+' '+op+' '+str(b)+" = ")
        constants.other.PRINT_LOCK.release()

        user_input_int = None
        try:
            user_input_int = int(user_input)
        except Exception as e:
            pass

        if user_input_int is None:
            common.general.safe_print("\nA valid input was not given. Aborting...\n\n\n")
            time.sleep(3)
            return
        elif user_input_int != solution:
            common.general.safe_print("\nI'm afraid that is incorrect. Aborting...\n\n\n")
            time.sleep(3)
            return
        else:
            common.general.safe_print("\nThat is correct. Executing...\n\n")
            time.sleep(3)

    filepath = bpy.path.abspath("//")
    current_filename = bpy.path.basename(bpy.data.filepath)
    extension = ".blend"
    if not current_filename.endswith(extension):
        raise Exception("Expected current Blender file to have '"+extension+"' for the extension.")
    new_filename = current_filename[:-len(extension)]+"_TEMP"+extension

    common.general.safe_print("Saving as temporary Blender file:")
    common.general.safe_print(filepath+new_filename)
    bpy.ops.wm.save_as_mainfile(filepath=filepath+new_filename, check_existing=False)
    common.general.safe_print("")

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    # First let's doublecheck we have an active scene.
    common.general.safe_print("Checking scene...")
    scene = bpy.context.scene
    if scene is None or not scene:
        raise Exception("No active scene.")

    # Next we find our collection.
    common.general.safe_print("Finding collection...")
    if constants.blender.COLLECTION_NAME not in scene.collection.children:
        raise Exception("Did not find collection '" + constants.blender.COLLECTION_NAME + "' in active scene.")
    collection = scene.collection.children[constants.blender.COLLECTION_NAME]

    # From there we find the layer collection that wraps it.
    common.general.safe_print("Finding layer collection of collection...")
    layer_collection = common.blender.find_layer_collection_of_collection(
        collection, bpy.context.view_layer.layer_collection)
    if layer_collection is None:
        raise Exception("Could not find layer collection of our collection.")

    # Next we find the master material.
    common.general.safe_print("Finding master material...")
    if constants.blender.MATERIAL_NAME not in bpy.context.blend_data.materials:
        raise Exception("Could not locate material '"+constants.blender.MATERIAL_NAME+"'.")
    master_material = bpy.context.blend_data.materials[constants.blender.MATERIAL_NAME]

    # Then we find the armature.
    common.general.safe_print("Finding armature...")
    if constants.blender.ARMATURE_NAME not in collection.all_objects:
        raise Exception("Could not locate armature '" + constants.blender.ARMATURE_NAME + "'.")
    armature = collection.all_objects[constants.blender.ARMATURE_NAME]

    common.general.safe_print("Modifying objects in collection...")
    for obj in collection.all_objects:
        common.general.safe_print("\tObject: "+obj.name)

        if obj.name in constants.blender.EVERYTHING:
            if type(obj.data) is bpy.types.Mesh:
                common.general.safe_print("\t\tDeleting all UV Maps except the master...")
                uv_layer_names = []
                for uv_layer in obj.data.uv_layers:
                    uv_layer_names.append(uv_layer.name)

                if constants.blender.UV_NAME in uv_layer_names:
                    uv_layer_names.remove(constants.blender.UV_NAME)
                    for uv_layer_name in uv_layer_names:
                        common.general.safe_print("\t\t\tRemoving '"+uv_layer_name+"'...")
                        obj.data.uv_layers.remove(obj.data.uv_layers[uv_layer_name])

                    common.general.safe_print("\t\tSetting the master UV Map as active...")
                    obj.data.uv_layers.active = obj.data.uv_layers[constants.blender.UV_NAME]

                    common.general.safe_print("\t\tRemoving all materials...")
                    obj.data.materials.clear()
                    common.general.safe_print("\t\tAdding the master material...")
                    obj.data.materials.append(master_material)
                else:
                    common.general.safe_print("\t\t\t??? This Mesh does not have the expected UV Map. Skipping...")
            else:
                common.general.safe_print("\t\t??? This is not a Mesh object. Skipping...")
        else:
            common.general.safe_print("\t\t??? Object is not in EVERYTHING. Skipping...")
    common.general.safe_print("Done modifying objects in collection.\n")

    if merge_meshes:
        bpy.ops.object.select_all(action="DESELECT")

        common.general.safe_print("Merging meshes. Selecting...")
        final_object = None

        for obj in collection.all_objects:
            common.general.safe_print("\tObject: " + obj.name)

            if obj.name in constants.blender.EVERYTHING:
                if type(obj.data) is bpy.types.Mesh:
                    if final_object is None:
                        final_object = obj
                        bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                else:
                    common.general.safe_print("\t\t??? This is not a Mesh object. Skipping...")
            else:
                common.general.safe_print("\t\t??? Object is not in EVERYTHING. Skipping...")

        common.general.safe_print("Objects selected. Merging...")
        bpy.ops.object.join()

        common.general.safe_print("Objects merged. Performing last changes...")

        bpy.ops.object.select_all(action="DESELECT")
        final_object.name = "MergedMesh"
        final_object.data.name = "Merged_mesh"
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        final_object.select_set(True)
        bpy.ops.object.parent_set(keep_transform=True)
        bpy.ops.object.select_all(action="DESELECT")

        # Clean up the empty empties.
        for obj in collection.all_objects:
            if len(obj.children) == 0 and obj.data is None:
                obj.select_set(True)
        bpy.ops.object.delete(use_global=True, confirm=False)
        bpy.ops.object.select_all(action="DESELECT")

        common.general.safe_print("Done.\n")

    bpy.ops.object.select_all(action="DESELECT")
    common.general.safe_print("Setting layer collection as active...")
    bpy.context.view_layer.active_layer_collection = layer_collection

    common.general.safe_print("Exporting FBX...")
    bpy.ops.export_scene.fbx(
        filepath=filepath+constants.blender.EXPORT_NAME+".fbx",
        path_mode="ABSOLUTE",
        check_existing=False,
        use_active_collection=True,
        apply_scale_options="FBX_SCALE_ALL",
        object_types={"EMPTY", "ARMATURE", "MESH", "OTHER"},
        use_mesh_modifiers=False,
        mesh_smooth_type="OFF", # Normals Only
        use_tspace=True,
        add_leaf_bones=True,
        use_armature_deform_only=True, # ???
        bake_anim=False,
        embed_textures=False,
        axis_forward='Z'
    )
    common.general.safe_print("")

    common.general.safe_print("Saving changes to temporary Blender file...")
    bpy.ops.wm.save_as_mainfile(check_existing=False)
    common.general.safe_print("")

    common.general.safe_print("Reloading original Blender file...")
    bpy.ops.wm.open_mainfile(filepath=filepath+current_filename)

    common.general.safe_print("\nExport complete.\n\n\n")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U00002714 Export complete.", is_silent=False)