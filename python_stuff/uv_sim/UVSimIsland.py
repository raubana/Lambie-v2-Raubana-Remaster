import random
import math

import mathutils

import common
import constants

import uv_sim.constants

try:
    import pygame
except:
    common.general.safe_print("WARNING: Couldn't import 'pygame'.")

try:
    import pymunk
except:
    common.general.safe_print("WARNING: Couldn't import module 'pymunk'.")


class UVSimIsland(object):
    def __init__(self, sim, obj, uv_layer, island):
        self.sim = sim
        self.obj = obj
        self.uv_layer = uv_layer
        self.island = island

        self.body = None
        self.center_offset = None

        self.initial_position = None

        self.usable_polys = []
        self.shapes = []

        self.determine_usable_polys()

        self.color = (random.randint(0, 255),
                      random.randint(0, 255),
                      random.randint(0, 255)
                      )
        self.poly_color = (
            int(common.new_math.lerp(255, self.color[0], 0.5)),
            int(common.new_math.lerp(255, self.color[1], 0.5)),
            int(common.new_math.lerp(255, self.color[2], 0.5))
        )
        self.line_color = (int(self.color[0] / 3), int(self.color[1] / 3), int(self.color[2] / 3))

        self.set_scale(1.0)

        bb = self.get_bb_of_shapes()
        self.fake_radius = math.sqrt((bb.right - bb.left) ** 2 + (bb.top - bb.bottom) ** 2)

        self.generate_sprite()

    def determine_usable_polys(self):
        # First we make a rect that forms the bounding box of the polygons.

        if not uv_sim.constants.HOLLOWOUTFATISLANDS:
            self.usable_polys = list(self.island)
            return

        br = None
        for poly in self.island:
            for loop_index in poly.loop_indices:
                uvloop = self.uv_layer.data[loop_index]

                new_rect = pygame.Rect(
                    int(uvloop.uv[0] * self.sim.sim_actual_size[0]),
                    int(uvloop.uv[1] * self.sim.sim_actual_size[1]),
                    0,
                    0
                )

                if br is None:
                    br = new_rect
                else:
                    br.union_ip(new_rect)

        # We use that bounding rect to make our main surface.
        line_thickness = int(max(self.sim.sim_actual_size) * 0.0025) + 2
        extra_space = line_thickness + 2
        main_surface = pygame.Surface(
            (
                br.width + (extra_space * 2),
                br.height + (extra_space * 2)
            )
        )
        main_surface.fill((0, 0, 0))
        main_surface.set_colorkey((0, 0, 0))

        # Next we draw every polygon from the island onto this main surface.
        for poly in self.island:
            points = []

            for loop_index in poly.loop_indices:
                uvloop = self.uv_layer.data[loop_index]

                points.append(
                    (
                        int(uvloop.uv[0] * self.sim.sim_actual_size[0] - br.left + extra_space),
                        int(uvloop.uv[1] * self.sim.sim_actual_size[1] - br.top + extra_space)
                    )
                )

            pygame.draw.polygon(main_surface, (255, 255, 255), points)
            pygame.draw.polygon(main_surface, (255, 255, 255), points, 1)

        # We generate a mask from this surface.
        main_mask = pygame.mask.from_surface(main_surface)

        # Next we make an outline mask.
        outline_mask = pygame.Mask(main_mask.get_size())

        for y in range(-1, 2):
            for x in range(-1, 2):
                outline_mask.draw(main_mask, (x, y))

        outline_mask.erase(main_mask, (0, 0))

        # We extend the 1 bits on the outline out two pixels in every direction.
        main_mask.clear()

        for y in range(-line_thickness, line_thickness + 1):
            for x in range(-line_thickness, line_thickness + 1):
                main_mask.draw(outline_mask, (x, y))

        outline_mask.clear()
        outline_mask.draw(main_mask, (0, 0))

        # Now we can go through and determine which polys are actually usable.
        del main_mask

        for poly in self.island:
            main_surface.fill((0, 0, 0))

            points = []

            for loop_index in poly.loop_indices:
                uvloop = self.uv_layer.data[loop_index]

                points.append(
                    (
                        int(uvloop.uv[0] * self.sim.sim_actual_size[0] - br.left + extra_space),
                        int(uvloop.uv[1] * self.sim.sim_actual_size[1] - br.top + extra_space)
                    )
                )

            pygame.draw.polygon(main_surface, (255, 255, 255), points)
            pygame.draw.polygon(main_surface, (255, 255, 255), points, 1)

            main_mask = pygame.mask.from_surface(main_surface)

            if main_mask.overlap(outline_mask, (0, 0)) is not None:
                self.usable_polys.append(poly)

    def set_scale(self, scale, radius=None, normalize_mass=True):
        if radius is None:
            radius = self.sim.sim_radius

        self.radius = radius
        self.scale = scale

        old_pos = None
        old_angle = None
        old_vel = None
        old_ang_vel = None
        if self.body is not None:
            old_pos = self.body.position
            old_angle = self.body.angle
            old_vel = self.body.velocity
            old_ang_vel = self.body.angular_velocity

            self.sim.space.remove(self.body)
            self.sim.space.remove(*self.shapes)

        self.body = pymunk.Body()

        self.shapes = []

        center = mathutils.Vector((0, 0, 0))
        weight = 0.0

        for poly in self.usable_polys:
            for loop_index in poly.loop_indices:
                uvloop = self.uv_layer.data[loop_index]
                v = mathutils.Vector(
                    (uvloop.uv[0] * self.sim.sim_actual_size[0], uvloop.uv[1] * self.sim.sim_actual_size[1], 0))

                center += v
                weight += 1

        center /= weight

        for shape in self.shapes:
            self.sim.remove_shape(shape)

        self.shapes = []
        total_mass = 0
        for poly in self.usable_polys:
            new_points = []

            for loop_index in poly.loop_indices:
                uvloop = self.uv_layer.data[loop_index]
                v = mathutils.Vector(
                    (uvloop.uv[0] * self.sim.sim_actual_size[0], uvloop.uv[1] * self.sim.sim_actual_size[1], 0))

                v -= center
                v *= scale
                v += center

                new_points.append((v[0], v[1]))

            shape = pymunk.Poly(self.body, new_points, radius=self.radius)

            self.sim.add_shape(shape)

            shape.friction = 0.0
            shape.elasticity = 0.75
            shape.density = 0.001

            total_mass += shape.mass

            self.shapes.append(shape)

        if normalize_mass:
            for shape in self.shapes:
                shape.mass = shape.mass / total_mass

        if old_pos is not None:
            self.body.position = old_pos
        if old_angle is not None:
            self.body.angle = old_angle
        if old_vel is not None:
            self.body.velocity = old_vel
        if old_ang_vel is not None:
            self.body.angular_velocity = old_ang_vel

        self.sim.space.add(self.body)
        self.sim.space.add(*self.shapes)

        if self.initial_position is None:
            self.initial_position = self.body.local_to_world(self.body.center_of_gravity)

    def get_bb_of_shapes(self):
        bb = self.shapes[0].bb
        left = min(bb.left, bb.right)
        top = max(bb.bottom, bb.top)
        right = max(bb.left, bb.right)
        bottom = min(bb.bottom, bb.top)

        for shape in self.shapes[1:]:
            bb2 = shape.bb

            left = min(left, bb2.left)
            top = max(top, bb2.top)
            right = max(right, bb2.right)
            bottom = min(bottom, bb2.bottom)

        return pymunk.BB(left, bottom, right, top)

    def generate_sprite(self):
        bb = self.get_bb_of_shapes()

        self.sprite = pygame.Surface(
            (
                int((bb.right - bb.left) * self.sim.scale[0] * uv_sim.constants.OVERSIZESPRITESCALE),
                int((bb.top - bb.bottom) * self.sim.scale[1] * uv_sim.constants.OVERSIZESPRITESCALE)
            ),
            pygame.SRCALPHA
        )

        if self.center_offset is None:
            self.center_offset = self.body.local_to_world(self.body.center_of_gravity) - bb.center()

        self.sprite.fill((self.poly_color[0], self.poly_color[1], self.poly_color[2], 0))

        for poly in self.island:
            points = []

            for loop_index in poly.loop_indices:
                uvloop = self.uv_layer.data[loop_index]

                points.append(
                    (
                        int((((uvloop.uv[0] * self.sim.sim_actual_size[0]) - bb.left)) / (
                                self.sim.sim_actual_size[0] / (uv_sim.constants.OVERSIZESPRITESCALE * self.sim.sim_size[0]))),
                        int((((uvloop.uv[1] * self.sim.sim_actual_size[1]) - bb.bottom)) / (
                                self.sim.sim_actual_size[1] / (uv_sim.constants.OVERSIZESPRITESCALE * self.sim.sim_size[1]))),
                    )
                )

            pygame.draw.polygon(self.sprite, self.line_color, points, 1)

        for shape in self.shapes:
            old_points = shape.get_vertices()

            points = []
            for point in old_points:
                point1 = point - pymunk.Vec2d(bb.left, bb.bottom)
                vec_scale = pymunk.Vec2d(self.sim.scale[0] * uv_sim.constants.OVERSIZESPRITESCALE,
                                         self.sim.scale[1] * uv_sim.constants.OVERSIZESPRITESCALE)

                point2 = pymunk.Vec2d(
                    point1.x * vec_scale.x,
                    point1.y * vec_scale.y
                )

                points.append((point2[0], point2[1]))

            pygame.draw.polygon(self.sprite, self.poly_color, points)

            if uv_sim.constants.PRETTY:
                pygame.draw.aalines(self.sprite, self.line_color, True, points)
            else:
                pygame.draw.polygon(self.sprite, self.line_color, points, 2)

        if uv_sim.constants.FORCE_SHOWCENTERS:
            point = self.body.local_to_world(self.body.center_of_gravity) - pymunk.Vec2d(bb.left, bb.bottom)

            scale = pymunk.Vec2d(self.sim.scale[0] * uv_sim.constants.OVERSIZESPRITESCALE, self.sim.scale[1] * uv_sim.constants.OVERSIZESPRITESCALE)
            point = pymunk.Vec2d(point.x * scale.x, point.y * scale.y)

            pygame.draw.circle(self.sprite, (0, 255, 0), (int(point.x), int(point.y)), 4 * uv_sim.constants.OVERSIZESPRITESCALE)

            pygame.draw.circle(self.sprite, (0, 0, 255),
                               (int(self.sprite.get_width() / 2), int(self.sprite.get_height() / 2)),
                               3 * uv_sim.constants.OVERSIZESPRITESCALE)

    def apply_to_uv_map(self):
        initial_pos = self.initial_position
        final_pos = self.body.local_to_world(self.body.center_of_gravity)

        m = mathutils.Matrix.Translation((
            (-initial_pos.x) / self.sim.sim_actual_size[0],
            (-initial_pos.y) / self.sim.sim_actual_size[1],
            0.0
        ))

        m = mathutils.Matrix.Rotation(self.body.angle, 4, 'Z') @ m

        m = mathutils.Matrix.Scale(self.scale, 4) @ m

        m = mathutils.Matrix.Translation((
            (final_pos.x) / self.sim.sim_actual_size[0],
            (final_pos.y) / self.sim.sim_actual_size[1],
            0.0
        )) @ m

        for i in range(len(self.island)):
            poly = self.island[i]

            for j in range(poly.loop_total):
                uvloop = self.uv_layer.data[j + poly.loop_start]

                new_uv = m @ mathutils.Vector((uvloop.uv.x, uvloop.uv.y, 0.0))

                uvloop.uv.x = new_uv.x
                uvloop.uv.y = new_uv.y

    def render(self):
        new_size = (int(self.sprite.get_width() * (self.scale / uv_sim.constants.OVERSIZESPRITESCALE)),
                    int(self.sprite.get_height() * (self.scale / uv_sim.constants.OVERSIZESPRITESCALE)))

        if uv_sim.constants.PRETTY:
            new_sprite = pygame.transform.smoothscale(self.sprite, new_size)
        else:
            new_sprite = pygame.transform.scale(self.sprite, new_size)
        new_sprite = pygame.transform.rotate(new_sprite, -math.degrees(self.body.angle))

        center = self.body.local_to_world(self.body.center_of_gravity - (self.center_offset * self.scale))
        scale = pymunk.Vec2d(self.sim.scale[0], self.sim.scale[1])
        center = pymunk.Vec2d(center.x * scale.x, center.y * scale.y)

        rect = new_sprite.get_rect(
            center=(
                int(center[0] + self.sim.sim_rect.left),
                int(center[1] + self.sim.sim_rect.top)
            )
        )

        self.sim.surface.blit(new_sprite, rect)

        if uv_sim.constants.FORCE_SHOWCENTERS:
            point = self.body.local_to_world(self.body.center_of_gravity)

            scale = pymunk.Vec2d(self.sim.scale[0], self.sim.scale[1])
            point = pymunk.Vec2d(point.x * scale.x, point.y * scale.y)

            point += pymunk.Vec2d(self.sim.sim_rect.left, self.sim.sim_rect.top)

            pygame.draw.circle(self.sim.surface, (255, 0, 0), (int(point.x), int(point.y)), 2)

    def render_radius(self):
        scale = pymunk.Vec2d(self.sim.scale[0], self.sim.scale[1])

        radius_color = (
            int(common.new_math.lerp(0, self.color[0], 0.5)),
            int(common.new_math.lerp(255, self.color[1], 0.5)),
            int(common.new_math.lerp(0, self.color[2], 0.5))
        )

        for shape in self.shapes:
            old_points = shape.get_vertices()
            new_points = []

            for i in range(len(old_points)):
                point_left = old_points[(i - 1) % len(old_points)]
                point_mid = old_points[i]
                point_right = old_points[(i + 1) % len(old_points)]

                vec_left = (point_left - point_mid).normalized()
                vec_right = (point_right - point_mid).normalized()

                normal_left = pymunk.Vec2d(-vec_left[1], vec_left[0])
                normal_right = pymunk.Vec2d(vec_right[1], -vec_right[0])

                normal = ((normal_left + normal_right) / 2.0).normalized()

                if normal_left.dot(normal_right) < 0:
                    point = (point_mid + (normal_left * self.radius)).rotated(self.body.angle) + self.body.position
                    point = pymunk.Vec2d(point.x * scale.x, point.y * scale.y)
                    point += pymunk.Vec2d(self.sim.sim_rect.left, self.sim.sim_rect.top)
                    new_points.append((point[0], point[1]))

                point = (point_mid + (normal * self.radius)).rotated(self.body.angle) + self.body.position
                point = pymunk.Vec2d(point.x * scale.x, point.y * scale.y)
                point += pymunk.Vec2d(self.sim.sim_rect.left, self.sim.sim_rect.top)
                new_points.append((point[0], point[1]))

                if normal_left.dot(normal_right) < 0:
                    point = (point_mid + (normal_right * self.radius)).rotated(self.body.angle) + self.body.position
                    point = pymunk.Vec2d(point.x * scale.x, point.y * scale.y)
                    point += pymunk.Vec2d(self.sim.sim_rect.left, self.sim.sim_rect.top)
                    new_points.append((point[0], point[1]))

            pygame.draw.polygon(self.sim.surface, radius_color, new_points)

    def render_radius_stats(self):
        center = self.body.local_to_world(self.body.center_of_gravity + (self.center_offset * self.scale))
        scale = pymunk.Vec2d(self.sim.scale[0], self.sim.scale[1])
        center = pymunk.Vec2d(center.x * scale.x, center.y * scale.y)

        text = self.sim.font.render(str(round(self.radius, 2)), uv_sim.constants.PRETTY, (255, 255, 255))

        rect = text.get_rect(
            center=(
                int(center[0] + self.sim.sim_rect.left),
                int(center[1] + self.sim.sim_rect.top)
            )
        )

        self.sim.surface.blit(text, rect)

    def render_debug(self):
        color = (255, 255, 0)

        if self.body.is_sleeping:
            color = (128, 128, 0)

        for shape in self.shapes:
            old_points = shape.get_vertices()
            new_points = []

            for point in old_points:
                point = point.rotated(self.body.angle) + self.body.position

                scale = pymunk.Vec2d(self.sim.scale[0], self.sim.scale[1])
                point = pymunk.Vec2d(point.x * scale.x, point.y * scale.y)

                point += pymunk.Vec2d(self.sim.sim_rect.left, self.sim.sim_rect.top)

                new_points.append((point[0], point[1]))

            pygame.draw.polygon(self.sim.surface, color, new_points, 1)

            if uv_sim.constants.PRETTY:
                pygame.draw.aalines(self.sim.surface, color, False, new_points)
