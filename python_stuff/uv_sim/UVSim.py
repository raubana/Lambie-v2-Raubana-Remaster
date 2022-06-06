import time
import random
import pygame
import pymunk

import bpy

import common

import uv_sim.constants
import uv_sim.UVSimIsland

if uv_sim.constants.EXPORTVIDEO:
    try:
        import cv2
    except:
        common.general.safe_print("WARNING: Couldn't import module 'cv2'.")


class UVSim(object):
    def __init__(self, window_size, sim_size, sim_actual_size, sim_radius, render_rate=5, export_rate=5,
                 export_frame_rate=60):
        pygame.init()

        self.window_size = window_size
        self.bg_color = (0, 0, 0)
        self.sim_size = sim_size

        self.sim_rect = pygame.Rect(0, 0, sim_size[0], sim_size[1])
        self.sim_rect.top = int((window_size[1] - sim_size[1]) / 2)
        self.sim_rect.right = int(window_size[0] - self.sim_rect.top)

        self.screen = pygame.display.set_mode(self.window_size)
        self.surface = pygame.Surface(self.window_size)
        self.render_rate = render_rate
        self.export_rate = export_rate
        self.export_frame_rate = export_frame_rate

        self.last_render = -100000000.0
        self.last_export = -100000000.0

        self.font = pygame.font.SysFont("", 32)

        self.sim_actual_size = sim_actual_size
        self.sim_radius = sim_radius
        self.step_size = 100

        self.sim_time = 0.0

        self.events = []

        self.scale = (
            self.sim_size[0] / float(sim_actual_size[0]),
            self.sim_size[1] / float(sim_actual_size[1])
        )

        self.space = pymunk.Space()

        self.space.damping = 1.0
        # space.gravity = (0.0, -1000.0)

        # self.space.iterations = 10
        # self.space.collision_bias = 0.00000001
        # self.space.collision_slop = 1000000

        self.space.idle_speed_threshold = 0.001
        self.space.sleep_time_threshold = 0.1

        self.wall_extra_thickness = max(sim_actual_size) * 0.05

        actual_thickness = self.wall_extra_thickness # + self.sim_radius
        wall_data = (
            ((-(actual_thickness * 2), -self.wall_extra_thickness),
             (sim_actual_size[0] + (actual_thickness * 2), -self.wall_extra_thickness)),
            ((sim_actual_size[0] + self.wall_extra_thickness, -(actual_thickness * 2)),
             (sim_actual_size[0] + self.wall_extra_thickness, sim_actual_size[1] + (actual_thickness * 2))),
            ((-(actual_thickness * 2), sim_actual_size[1] + self.wall_extra_thickness),
             (sim_actual_size[0] + (actual_thickness * 2), sim_actual_size[1] + self.wall_extra_thickness)),
            ((-self.wall_extra_thickness, -(actual_thickness * 2)),
             (-self.wall_extra_thickness, sim_actual_size[1] + (actual_thickness * 2)))
        )

        self.next_shape_id = 0
        self.shape_dict = {}

        self.total_collisions = 0
        self.total_collisions_in_cache = 0

        self.collisions = {}
        if uv_sim.constants.FORCE_SHOWCOLLISIONS:
            self.collision_cache = {}

        self.walls = []
        for data in wall_data:
            shape = pymunk.Segment(self.space.static_body, data[0], data[1], actual_thickness)

            self.walls.append(shape)

            self.add_shape(shape)
            shape.uvsim_body = None

            shape.elasticity = 0.75
            shape.friction = 0.0
            self.space.add(shape)

        self.bodies = []

        self.escaped_bodies_check_freq = 1.0
        self.last_checked_escaped_bodies = -100000000.0

        self.messages = {}

        self.set_message("COLLISIONS: ", 0)
        if uv_sim.constants.FORCE_SHOWCOLLISIONS:
            self.set_message("COLLISION CACHE: ", 0)

        if uv_sim.constants.EXPORTVIDEO:
            self.export = cv2.VideoWriter(bpy.path.abspath("//") + "output.avi",
                                          cv2.VideoWriter_fourcc(*"MJPG"),
                                          export_frame_rate,
                                          self.window_size
                                          )

            attempts = 10
            while attempts > 0:
                time.sleep(0.1)
                if not self.export.isOpened():
                    common.general.safe_print("failed to init", attempts)
                    attempts -= 1
                else:
                    break

        handler = self.space.add_default_collision_handler()
        handler.begin = self.handle_collision_start
        handler.separate = self.handle_collision_end

    def handle_collision_start(self, arbiter, space, data):
        older_shape = arbiter.shapes[0]
        newer_shape = arbiter.shapes[1]
        if arbiter.shapes[1].custom_id < arbiter.shapes[0].custom_id:
            older_shape = arbiter.shapes[1]
            newer_shape = arbiter.shapes[0]

        if older_shape.custom_id in self.collisions:
            # A key already exists for this older shape, meaning it had a collision recently.
            if newer_shape.custom_id in self.collisions[older_shape.custom_id]:
                # The collision between these two shapes already exists. Skip it.
                pass
            else:
                # Need to add this newer shape to the older shapes' collisions.
                self.collisions[older_shape.custom_id].append(newer_shape.custom_id)
                self.total_collisions += 1

                if older_shape.uvsim_body is not None:
                    older_shape.uvsim_body.num_collisions += 1
                if newer_shape.uvsim_body is not None:
                    newer_shape.uvsim_body.num_collisions += 1
        else:
            # A key doesn't exist for this older shape yet, so we have to make one and add the newer shape to its'
            # collisions.
            self.collisions[older_shape.custom_id] = [newer_shape.custom_id, ]
            self.total_collisions += 1

            if older_shape.uvsim_body is not None:
                older_shape.uvsim_body.num_collisions += 1
            if newer_shape.uvsim_body is not None:
                newer_shape.uvsim_body.num_collisions += 1

        if uv_sim.constants.FORCE_SHOWCOLLISIONS:
            if older_shape.custom_id in self.collision_cache:
                # A key already exists for this older shape, meaning it had a collision since the last frame.
                if newer_shape.custom_id in self.collision_cache[older_shape.custom_id]:
                    # The collision between these two shapes already exists. Skip it.
                    pass
                else:
                    # Need to add this newer shape to the older shapes' collisions.
                    self.collision_cache[older_shape.custom_id].append(newer_shape.custom_id)
                    self.total_collisions_in_cache += 1
            else:
                # A key doesn't exist for this older shape yet, so we have to make one and add the newer shape to
                # its' collisions.
                self.collision_cache[older_shape.custom_id] = [newer_shape.custom_id, ]
                self.total_collisions_in_cache += 1

        return True

    def handle_collision_end(self, arbiter, space, data):
        older_shape = arbiter.shapes[0]
        newer_shape = arbiter.shapes[1]
        if arbiter.shapes[1].custom_id < arbiter.shapes[0].custom_id:
            older_shape = arbiter.shapes[1]
            newer_shape = arbiter.shapes[0]

        if older_shape.custom_id in self.collisions:
            if newer_shape.custom_id in self.collisions[older_shape.custom_id]:
                self.collisions[older_shape.custom_id].remove(newer_shape.custom_id)
                self.total_collisions -= 1

                if older_shape.uvsim_body is not None:
                    older_shape.uvsim_body.num_collisions -= 1
                if newer_shape.uvsim_body is not None:
                    newer_shape.uvsim_body.num_collisions -= 1

                # If we end up emptying this list of collisions for this shape, we'll remove it from the dictionary
                # of collisions.
                if len(self.collisions[older_shape.custom_id]) == 0:
                    del self.collisions[older_shape.custom_id]
        else:
            common.general.safe_print("Hmm, that wasn't supposed to happen.")

    def add_shape(self, shape):
        shape.custom_id = self.next_shape_id
        self.shape_dict[shape.custom_id] = shape
        self.next_shape_id += 1

    def remove_shape(self, shape):
        if shape.custom_id in self.shape_dict:
            del self.shape_dict[shape.custom_id]

    def set_message(self, variable, value):
        self.messages[variable] = value

    def remove_message(self, variable):
        if variable in self.messages:
            del self.messages[variable]

    def set_damping(self, damping):
        self.space.damping = damping

    def add_island(self, obj, uv_layer, island):
        body = uv_sim.UVSimIsland.UVSimIsland(self, obj, uv_layer, island)
        self.bodies.append(body)

    def set_island_scale(self, scale):
        for body in self.bodies:
            body.set_scale(scale, min(scale, 1.0) * self.sim_radius)

    def reset_sim_time(self):
        self.last_checked_escaped_bodies = -100000000.0
        self.last_render = -100000000.0
        self.last_export = -100000000.0
        self.sim_time = 0.0

    def nudge_body(self, body, force_scale=1.0):
        radius = body.fake_radius
        mass = body.body.mass

        max_force = (mass ** 1.25) * 0.00025 * force_scale
        max_offset = radius

        body.body.apply_impulse_at_local_point(
            ((random.random() * 2 - 1) * self.sim_actual_size[0] * max_force,
             (random.random() * 2 - 1) * self.sim_actual_size[1] * max_force),
            ((random.random() * 2 - 1) * max_offset, (random.random() * 2 - 1) * max_offset)
        )

    def nudge_islands(self, force_scale=1.0):
        for body in self.bodies:
            self.nudge_body(body, force_scale)

    def nudge_touching_islands(self, force_scale=1.0):
        matches = []

        for older_shape_id in self.collisions:
            if self.shape_dict[older_shape_id].body not in matches:
                matches.append(self.shape_dict[older_shape_id].body)

            for newer_shape_id in self.collisions[older_shape_id]:
                if self.shape_dict[newer_shape_id].body not in matches:
                    matches.append(self.shape_dict[newer_shape_id].body)

        for body in self.bodies:
            if body.body in matches:
                self.nudge_body(body, force_scale)

    def mix_islands(self):
        world_center = pymunk.Vec2d(self.sim_actual_size[0] / 2, self.sim_actual_size[1] / 2)

        for body in self.bodies:
            pos = body.body.local_to_world(body.body.center_of_gravity)

            dif = pos - world_center
            dif_norm = dif.normalized()

            turned = pymunk.Vec2d(dif[1], -dif[0])
            turned_norm = turned.normalized()

            mass2 = (body.body.mass ** 0.9)

            body.body.apply_impulse_at_world_point(
                turned * mass2 * (0.5 / max(self.sim_actual_size)),
                pos + (turned_norm * max(self.sim_actual_size) * 0.01)
            )

    def quit(self):
        self.finish_export()
        pygame.quit()
        del self.space

    def update(self):
        self.events = pygame.event.get()

        self.set_message("COLLISIONS: ", self.total_collisions)
        if uv_sim.constants.FORCE_SHOWCOLLISIONS:
            self.set_message("COLLISION CACHE: ", self.total_collisions_in_cache)

        for e in self.events:
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                self.quit()
                return

        dt = 1.0 / float(self.step_size)

        self.space.step(dt)
        self.sim_time += dt

        for body in self.bodies:
            oob_level0 = 0
            oob_level1 = 0
            oob_level2 = 0

            pos = body.body.local_to_world(body.body.center_of_gravity)
            radius = body.fake_radius * body.scale

            if pos.x <= radius or pos.y <= radius or \
            pos.x >= self.sim_actual_size[0] - radius or \
            pos.y >= self.sim_actual_size[1] - radius:

                for shape in body.shapes:
                    bb = shape.bb
                    if bb.left < 0 or bb.bottom < 0 or \
                    bb.right > self.sim_actual_size[0] or bb.top > self.sim_actual_size[1]:

                        if bb.right < 0 or bb.top < 0 or \
                        bb.left > self.sim_actual_size[0] or bb.bottom > self.sim_actual_size[1]:
                            oob_level2 += 1
                        else:
                            oob_level1 += 1
                    else:
                        oob_level0 += 1
            else:
                oob_level0 += len(body.shapes)

            if oob_level0 == 0 and oob_level1 == 0 and oob_level2 > 0:
                body.out_of_bounds_level = 3
            elif oob_level2 > 0:
                body.out_of_bounds_level = 2
            elif oob_level1 > 0:
                body.out_of_bounds_level = 1
            else:
                body.out_of_bounds_level = 0

        dif = self.sim_time - self.last_checked_escaped_bodies

        if int(dif / self.escaped_bodies_check_freq) > 0:
            self.last_checked_escaped_bodies = self.sim_time

            for body in self.bodies:
                if body.out_of_bounds_level >= 3:
                    common.general.safe_print("Body escaped. Moving back inside the sim...")

                    new_pos = pymunk.Vec2d(self.sim_actual_size[0] / 2, self.sim_actual_size[1] / 2)
                    new_pos += pymunk.Vec2d((random.random() * 2 - 1) * self.sim_actual_size[0] * 0.1,
                                            (random.random() * 2 - 1) * self.sim_actual_size[1] * 0.1)

                    body.body.position = body.body.world_to_local(new_pos)

                    self.space.reindex_shapes_for_body(body.body)

                    break

    def render(self, force_render=False, show_sprites=True, show_debug=False, show_radius=False, show_collisions=True):
        dif1 = self.sim_time - self.last_render
        dif2 = self.sim_time - self.last_export

        if int(dif1 * self.render_rate) > 0 or force_render:
            self.last_render = self.sim_time

            self.surface.fill(self.bg_color)

            scale = pymunk.Vec2d(self.scale[0], self.scale[1])

            if not uv_sim.constants.FORCE_HIDEEXPENSIVERENDERING:
                if show_radius:
                    for wall in self.walls:
                        a = (
                            int(wall.a.x * scale.x + self.sim_rect.left),
                            int(wall.a.y * scale.y + self.sim_rect.top)
                        )

                        b = (
                            int(wall.b.x * scale.x + self.sim_rect.left),
                            int(wall.b.y * scale.y + self.sim_rect.top)
                        )

                        pygame.draw.line(self.surface, (0, 128, 0), a, b,
                                         int((self.wall_extra_thickness + self.sim_radius) * 2 * min(self.scale)))

                        if uv_sim.constants.PRETTY:
                            pygame.draw.circle(self.surface, (0, 128, 0), a,
                                               int((self.wall_extra_thickness + self.sim_radius) * min(self.scale)))
                            pygame.draw.circle(self.surface, (0, 128, 0), b,
                                               int((self.wall_extra_thickness + self.sim_radius) * min(self.scale)))

                for wall in self.walls:
                    a = (
                        int(wall.a.x * scale.x + self.sim_rect.left),
                        int(wall.a.y * scale.y + self.sim_rect.top)
                    )

                    b = (
                        int(wall.b.x * scale.x + self.sim_rect.left),
                        int(wall.b.y * scale.y + self.sim_rect.top)
                    )

                    pygame.draw.line(self.surface, (32, 32, 32), a, b,
                                     int(self.wall_extra_thickness * 2 * min(self.scale)))

                    if uv_sim.constants.PRETTY:
                        pygame.draw.circle(self.surface, (32, 32, 32), a,
                                           int(self.wall_extra_thickness * min(self.scale)))
                        pygame.draw.circle(self.surface, (32, 32, 32), b,
                                           int(self.wall_extra_thickness * min(self.scale)))

            sim_rect = pygame.Rect(
                self.sim_rect.left - 1,
                self.sim_rect.top - 1,
                self.sim_rect.width + 2,
                self.sim_rect.height + 2
            )

            pygame.draw.rect(self.surface, (255, 255, 255), sim_rect, 1)

            if show_radius and not uv_sim.constants.FORCE_HIDEEXPENSIVERENDERING:
                for body in self.bodies:
                    body.render_radius()

            if show_sprites or uv_sim.constants.FORCE_HIDEEXPENSIVERENDERING:
                for body in self.bodies:
                    body.render()

            if (show_debug and not uv_sim.constants.FORCE_HIDEEXPENSIVERENDERING) or uv_sim.constants.FORCE_SHOWDEBUG:
                for body in self.bodies:
                    body.render_debug()

            if show_collisions and uv_sim.constants.FORCE_SHOWCOLLISIONS:
                for older_shape_id in self.collision_cache:
                    shape1 = self.shape_dict[older_shape_id]

                    center1 = shape1.body.local_to_world(shape1.center_of_gravity)
                    center1 = pymunk.Vec2d(center1.x * scale.x, center1.y * scale.y)
                    center1_screen = (
                        int(center1[0] + self.sim_rect.left),
                        int(center1[1] + self.sim_rect.top)
                    )

                    for newer_shape_id in self.collision_cache[older_shape_id]:
                        shape2 = self.shape_dict[newer_shape_id]

                        center2 = shape2.body.local_to_world(shape2.center_of_gravity)
                        center2 = pymunk.Vec2d(center2.x * scale.x, center2.y * scale.y)
                        center2_screen = (
                            int(center2[0] + self.sim_rect.left),
                            int(center2[1] + self.sim_rect.top)
                        )

                        radius = 2
                        color = (255, 0, 0)

                        if uv_sim.constants.PRETTY:
                            # pygame.draw.circle( self.surface, color, center1_screen, radius )
                            # pygame.draw.circle( self.surface, color, center2_screen, radius )
                            pygame.draw.aaline(self.surface, color, center1_screen, center2_screen)
                        else:
                            pygame.draw.line(self.surface, color, center1_screen, center2_screen)

            if show_radius and not uv_sim.constants.FORCE_HIDEEXPENSIVERENDERING:
                for body in self.bodies:
                    body.render_radius_stats()

            if uv_sim.constants.FORCE_SHOWCOLLISIONS:
                self.collision_cache = dict(self.collisions)
                self.total_collisions_in_cache = self.total_collisions
                # self.collision_cache = list( self.collisions )

            x, y = 16, 16

            for key, val in self.messages.items():
                text_surf = self.font.render(key + str(val), uv_sim.constants.PRETTY, (255, 255, 255))
                rect = text_surf.get_rect(topleft=(x, y))
                self.surface.blit(text_surf, rect)

                y += int(self.font.get_height() * 1.5)

            self.screen.blit(self.surface, (0, 0))
            pygame.display.flip()

            if uv_sim.constants.EXPORTVIDEO:
                if int(dif2 * self.export_rate) > 0:
                    self.last_export = self.sim_time

                    frame = self.surface.convert()

                    attempts = 10
                    while attempts > 0:
                        try:
                            pygame.image.save(frame, bpy.path.abspath("//") + "output.bmp")
                            break
                        except Exception as e:
                            common.general.safe_print(e)
                            common.general.safe_print("failed to save", attempts)
                            attempts -= 1
                            time.sleep(0.1)

                    attempts = 10
                    while attempts > 0:
                        try:
                            img = cv2.imread(bpy.path.abspath("//") + "output.bmp", -1)
                            break
                        except Exception as e:
                            common.general.safe_print(e)
                            common.general.safe_print("failed to load", attempts)
                            attempts -= 1
                            time.sleep(0.1)

                    self.export.write(img)

                    del frame
                    del img

    def finish_export(self):
        if uv_sim.constants.EXPORTVIDEO:
            attempts = 10
            while attempts > 0:
                self.export.release()
                time.sleep(0.1)

                if self.export.isOpened():
                    attempts -= 1
                    common.general.safe_print("failed to release", attempts)
                else:
                    break
