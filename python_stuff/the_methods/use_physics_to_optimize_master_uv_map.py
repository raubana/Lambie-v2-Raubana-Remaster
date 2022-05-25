import time

import bpy

import pygame

import common
import constants

import notifications
import uv_sim


def run(skip_mixing=False, skip_shaking_up=False, skip_scaling=False,
                                          skip_maximize_radius=True, auto_apply=False, leave_all_selected=False):
    common.general.safe_print("")
    common.general.safe_print(" ===   Using Physics to Optimize Master UV Map   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U0001F9F1 Using physics to optimize the master UV map", is_silent=False)

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Prepping the physics simulation...")
    sim = uv_sim.UVSim.UVSim((1200, 800), (700, 700), constants.texture.TEXTURE_SIZE, max(constants.texture.TEXTURE_SIZE) * constants.uv.UV_MARGIN)

    for obj_name in constants.blender.EVERYTHING:
        obj = bpy.context.view_layer.objects[obj_name]
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Creating physics bodies for object '" + obj_name + "'...")

        # Weirdly, has to be in object mode to work.
        islands = common.blender.get_uv_islands(obj)

        for island_i in range(len(islands)):
            if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- island", island_i, "/", len(islands))

            sim.add_island(obj, obj.data.uv_layers[constants.uv.UV_NAME], islands[island_i])

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Simulation prepped. Running simulation...")

    sim.set_message("Status: ", "Prepped")
    sim.set_message("Notes: ", "")

    sim.reset_sim_time()

    if uv_sim.constants.CINEMATICSEQUENCES:
        sim_duration = (sim.export_frame_rate / sim.export_rate) * 5
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_collisions=False)

        sim.reset_sim_time()
        sim.set_message("Starting in ", 3)
        sim_duration = (sim.export_frame_rate / sim.export_rate)
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_radius=True)

        sim.reset_sim_time()
        sim.set_message("Starting in ", 2)
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_radius=True)

        sim.reset_sim_time()
        sim.set_message("Starting in ", 1)
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_radius=True)

        sim.reset_sim_time()
        sim.set_damping(0.5)

    sim.remove_message("Starting in ")

    sim.set_message("Time: ", 0.0)
    sim.set_message("Damping: ", round(sim.space.damping, 4))
    sim.set_message("Scale: ", 1.0)
    sim.set_message("Radius: ", round(sim.sim_radius, 4))

    last_scale = 1.0
    current_scale = 1.0
    reverse = False

    if not skip_mixing:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("- \U0001f963 Mixing")

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Reducing scale...")

        sim.set_message("Status: ", "Reducing Scale")

        while current_scale > 0.5:
            sim.reset_sim_time()

            current_scale -= 0.01
            sim.set_island_scale(current_scale)
            sim.set_message("Scale: ", round(current_scale, 4))
            sim_duration = 1.0
            while sim.sim_time < sim_duration:
                sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
                sim.update()
                sim.render(show_radius=True)

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Mixing islands...")

        current_scale = 0.5
        sim.set_island_scale(current_scale)
        sim.set_message("Scale: ", round(current_scale, 4))

        sim.reset_sim_time()
        sim.set_damping(1.0)
        sim.set_message("Damping: ", round(sim.space.damping, 4))
        sim.set_message("Status: ", "Mixing Islands")
        sim_duration = 120.0
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))

            sim.mix_islands()
            sim.update()
            sim.render()

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Slowly increasing scale to 1.0...")

        sim.reset_sim_time()
        sim.set_damping(0.99)
        sim.set_message("Damping: ", round(sim.space.damping, 4))
        sim.set_message("Status: ", "Slowly Increasing Island Scale")

        while current_scale < 1.0:
            sim.reset_sim_time()

            current_scale += 0.01
            sim.set_island_scale(current_scale)
            sim.set_message("Scale: ", round(current_scale, 4))

            sim.nudge_islands()

            sim_duration = 5.0
            while sim.sim_time < sim_duration:
                sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
                sim.mix_islands()
                sim.update()
                sim.render(show_radius=True)

        current_scale = 1.0

        sim.set_island_scale(1.0)
        sim.set_message("Scale: ", round(current_scale, 4))

    if not skip_shaking_up:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("- \U0001f91d Shaking up")

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Shaking things up a bit...")
        sim.reset_sim_time()
        sim.set_damping(0.9)
        sim.set_message("Damping: ", round(sim.space.damping, 4))
        sim.set_message("Status: ", "Shaking Things Up")
        sim_duration = 120.0
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.nudge_islands(force_scale=common.new_math.lerp(1.0, 0.0, 1 - (1 - (sim.sim_time / sim_duration)) ** 2))
            sim.update()
            sim.render()

    if not skip_scaling:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("- \U00002696 Scaling")

        successful_iterations = 0
        unsuccessful_iterations = 0

        sim.set_message("Successful Iterations: ", successful_iterations)
        sim.set_message("Unsuccessful Iterations: ", unsuccessful_iterations)
        sim.set_message("Direction: ", "Increasing Scale")

        sim.set_damping(0.25)
        sim.set_message("Damping: ", round(sim.space.damping, 4))

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Testing scales...")
        while True:
            if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Testing scale", current_scale, "...")
            # Update the simulation until every body is sleeping or we pass the max number of iterations.
            success = False
            at_rest = False
            touching = True
            iterations = 0

            last_time = time.time()
            last_percent = 0

            sim.reset_sim_time()
            sim.set_message("Status: ", "Shaking Before Test")

            sim_duration = 1.0

            while sim.sim_time < sim_duration:
                sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
                sim.nudge_islands(force_scale=common.new_math.lerp(0.1, 0.0, 1 - (1 - (sim.sim_time / sim_duration)) ** 2))
                sim.update()
                sim.render()

            sim.reset_sim_time()
            sim.set_message("Status: ", "Testing")

            min_sim_time = 15.0
            max_sim_time = 100.0

            while (not success or (sim.sim_time <= min_sim_time)) and (sim.sim_time < max_sim_time or not touching):
                at_rest = True
                touching = False
                success = True

                sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(max_sim_time, 1)))

                sim.update()
                sim.render()

                if sim.sim_time >= min_sim_time:
                    for body in sim.bodies:
                        if not body.body.is_sleeping:
                            at_rest = False
                            break

                    touching = sim.total_collisions > 0

                    if not at_rest:
                        success = False
                        sim.set_message("Notes: ", "Island not at rest.")
                    elif touching:
                        success = False
                        sim.set_message("Notes: ", "Island touching something.")

                        # sim.nudge_sleeping_and_touching_islands( force_scale=0.1 )

                        original_sim_time = sim.sim_time

                        sim.reset_sim_time()

                        matches = []

                        for older_shape_id in sim.collisions:
                            if sim.shape_dict[older_shape_id].body not in matches:
                                matches.append(sim.shape_dict[older_shape_id].body)

                            for newer_shape_id in sim.collisions[older_shape_id]:
                                if sim.shape_dict[newer_shape_id].body not in matches:
                                    matches.append(sim.shape_dict[newer_shape_id].body)

                        for body in sim.bodies:
                            if body.body in matches:
                                body.set_scale(body.scale, sim.sim_radius + 1)

                        sim_duration = 10.0

                        while sim.sim_time < sim_duration:
                            sim.set_message("Sub-Time: ",
                                            str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
                            sim.update()
                            sim.render()

                        sim.remove_message("Sub-Time: ")

                        for body in sim.bodies:
                            body.set_scale(body.scale)

                        sim.reset_sim_time()

                        sim.sim_time = original_sim_time + 5

                    if success:
                        for body in sim.bodies:
                            for shape in body.shapes:
                                bb = shape.bb
                                if bb.left < 0 or bb.bottom < 0 or bb.right > sim.sim_actual_size[0] or bb.top > \
                                        sim.sim_actual_size[1]:
                                    if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(
                                        "---- Was marked successful but has shapes outside simulation bounds.")
                                    sim.set_message("Notes: ", "Island not contained by sim. bounds.")
                                    success = False
                                    break

                    if success:
                        sim.set_message("Notes: ", "")
                else:
                    sim.set_message("Notes: ", "Waiting until min. sim. time.")

            last_scale = current_scale

            if success:
                if reverse:
                    successful_iterations += 1

                    if successful_iterations >= 1:
                        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- Managed to work with scale", last_scale,
                                                          ". Breaking out...")
                        break
                else:
                    successful_iterations += 1
                    unsuccessful_iterations = 0

                    current_scale += 0.005
            else:
                if reverse:
                    unsuccessful_iterations += 1

                    if unsuccessful_iterations >= 2:
                        current_scale -= 0.001
                        successful_iterations = 0
                        unsuccessful_iterations = 0

                    if current_scale <= 1.0:
                        sim.quit()
                        raise Exception("Failed to use physics to optimize the UV map.")
                else:
                    successful_iterations = 0
                    unsuccessful_iterations += 1

                    if unsuccessful_iterations >= 2:
                        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
                            "- \U000021a9 Got to scale '" + str(
                                round(current_scale, 4)) + "' before reversing")

                        if constants.other.VERBOSE_LEVEL >= 3: common.general.safe_print(" --- No success at scale", current_scale, ", reversing...")

                        reverse = True

                        successful_iterations = 0
                        unsuccessful_iterations = 0

                        sim.set_message("Status: ", "Reversing")
                        sim.set_message("Notes: ", "")
                        sim.set_message("Direction: ", "Decreasing Scale")

                        if uv_sim.constants.CINEMATICSEQUENCES:
                            sim.reset_sim_time()

                            sim_duration = (sim.export_frame_rate / sim.export_rate) * 5.0
                            while sim.sim_time < sim_duration:
                                sim.set_message("Time: ",
                                                str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
                                sim.update()
                                sim.render(show_radius=True)

                        current_scale -= 0.001

            sim.set_message("Successful Iterations: ", successful_iterations)
            sim.set_message("Unsuccessful Iterations: ", unsuccessful_iterations)

            if current_scale != last_scale:
                sim.set_island_scale(current_scale)
                sim.set_message("Scale: ", round(current_scale, 4))

    sim.remove_message("Successful Iterations: ")
    sim.remove_message("Unsuccessful Iterations: ")
    sim.remove_message("Direction: ")

    if not skip_maximize_radius:
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("- \U0001f388 Maximizing radius")

        if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Maximizing the radius of the islands...")
        sim.set_message("Status: ", "Maximizing Island Radius")

        sim.set_damping(0.25)
        sim.set_message("Damping: ", round(sim.space.damping, 4))

        iterations_without_change = 0

        sim.set_message("Iterations Without Change: ", iterations_without_change)
        sim.set_message("Direction: ", "Increasing Radius")

        while True:
            collided_bodies = []

            sim.reset_sim_time()
            sim_duration = 0.2
            sim.set_message("Time: ", str(round(sim_duration, 2)))
            sim.nudge_touching_islands(force_scale=0.1)

            while sim.sim_time < sim_duration:
                sim.update()

                for older_shape_id in sim.collisions:
                    body1 = sim.shape_dict[older_shape_id].body

                    if body1 not in collided_bodies:
                        collided_bodies.append(body1)

                    for newer_shape_id in sim.collisions[older_shape_id]:
                        body2 = sim.shape_dict[newer_shape_id].body

                        if body2 not in collided_bodies:
                            collided_bodies.append(body2)

                sim.render(show_radius=True)

            for body in sim.bodies:
                body_is_clipping = False
                for shape in body.shapes:
                    bb = shape.bb
                    if bb.left < 0 or bb.bottom < 0 or bb.right > sim.sim_actual_size[0] or bb.top > \
                            sim.sim_actual_size[1]:
                        body_is_clipping = True
                        break
                if body_is_clipping and body.body not in collided_bodies:
                    collided_bodies.append(body.body)

            changes = False

            for body in sim.bodies:
                if body.body not in collided_bodies:
                    body.set_scale(body.scale, body.radius + 0.5)
                    changes = True

            if not changes:
                iterations_without_change += 1
            else:
                iterations_without_change = max(iterations_without_change - 1, 0)

            sim.set_message("Iterations Without Change: ", iterations_without_change)

            if constants.other.VERBOSE_LEVEL >= 4: common.general.safe_print(" ---- Iterations without change:", iterations_without_change)

            if iterations_without_change >= 25:
                break

        sim.remove_message("Iterations Without Change: ")
        sim.remove_message("Direction: ")

    if constants.other.VERBOSE_LEVEL >= 2: common.general.safe_print(" -- Done testing. Finishing up...")

    if uv_sim.constants.CINEMATICSEQUENCES:
        sim.reset_sim_time()
        sim.set_message("Status: ", "Wrapping Up")
        sim.set_damping(0.025)
        sim.set_message("Damping: ", round(sim.space.damping, 4))

        sim_duration = (sim.export_frame_rate / sim.export_rate) * 10
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_sprites=False, show_debug=True, show_radius=True)

    sim.reset_sim_time()
    sim.set_message("Status: ", "Done")

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")

    if uv_sim.constants.CINEMATICSEQUENCES:
        sim_duration = (sim.export_frame_rate / sim.export_rate) * 5
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_debug=True, show_collisions=False)

        sim.reset_sim_time()

        sim_duration = (sim.export_frame_rate / sim.export_rate) * 10
        while sim.sim_time < sim_duration:
            sim.set_message("Time: ", str(round(sim.sim_time, 1)) + "/" + str(round(sim_duration, 1)))
            sim.update()
            sim.render(show_collisions=False)

    if not auto_apply:
        if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Waiting for user input in sim window...")
        if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("- \U000026a0 WAITING FOR USER INPUT",
                                                                         is_silent=False)

    sim.set_message("Status: ", "Waiting For User Input")

    sim.remove_message("Damping: ")
    sim.remove_message("Radius: ")

    sim.set_message("F5: ", "Apply UVs")
    sim.set_message("F9: ", "Continue")

    sim.bg_color = (0, 64, 0)

    running_loop = True
    apply_uvs = auto_apply
    while running_loop:
        if apply_uvs or auto_apply:
            for body in sim.bodies:
                body.apply_to_uv_map()

            sim.set_message("Notes: ", "UVs have been changed.")
            apply_uvs = False

        sim.update()
        sim.render()

        for e in sim.events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F5:
                    apply_uvs = True
                    sim.set_message("Notes: ", "Applying UVs...")
                elif e.key == pygame.K_F9:
                    running_loop = False

        if auto_apply:
            running_loop = False

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Closing sim...")
    sim.quit()
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    if leave_all_selected:
        for i in range(len(constants.blender.EVERYTHING)):
            object_name = constants.blender.EVERYTHING[i]
            obj = bpy.context.view_layer.objects[object_name]
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U00002714 Finished using physics to optimize the master UV map", is_silent=False)
