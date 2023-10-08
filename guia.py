from manim import *
import operator as op
class Wall(Line):
    CONFIG = {
        "tick_spacing": 0.5,
        "tick_length": 0.25,
        "tick_style": {
            "stroke_width": 1,
            "stroke_color": WHITE,
        },
    }

    def __init__(self, height, **kwargs):
        Line.__init__(self, ORIGIN, height * UP, **kwargs)
        self.height = height
        self.ticks = self.get_ticks()
        self.add(self.ticks)

    def get_ticks(self):
        n_lines = int(self.height / self.CONFIG['tick_spacing'])
        lines = VGroup(*[
            Line(ORIGIN, self.tick_length * UR).shift(n * self.CONFIG['tick_spacing'] * UP)
            for n in range(n_lines)
        ])
        lines.set_style(**self.tick_style)
        lines.move_to(self, DR)
        return lines
class Block(Square):
    CONFIG = {
        "mass": 1,
        "velocity": 0,
        "width": None,
        "label_text": None,
        "label_scale_value": 0.8,
        "fill_opacity": 1,
        "stroke_width": 3,
        "stroke_color": WHITE,
        "fill_color": None,
        "sheen_direction": UL,
        "sheen_factor": 0.5,
        "sheen_direction": UL,
    }

    def __init__(self, **kwargs):
        if self.CONFIG['width'] is None:
            self.CONFIG['width'] = self.mass_to_width(self.CONIFG['mass'])
        if self.CONFIG['fill_color'] is None:
            self.CONFIG['fill_color'] = self.mass_to_color(self.CONFIG['mass'])
        if self.CONFIG['label_text'] is None:
            self.CONFIG['label_text'] = self.mass_to_label_text(self.CONFIG['mass'])
        if "width" in kwargs:
            kwargs.pop("width")
        Square.__init__(self, side_length=self.width, **kwargs)
        self.label = self.get_label()
        self.add(self.label)

    def get_label(self):
        label = Tex(self.CONFIG['label_text'])
        label.scale(self.CONFIG['label_scale_value'])
        label.next_to(self, UP, SMALL_BUFF)
        return label

    def get_points_defining_boundary(self):
        return self.points

    def mass_to_color(self, mass):
        colors = [
            LIGHT_GREY,
            BLUE_D,
            BLUE_D,
            BLUE_E,
            BLUE_E,
            DARK_GREY,
            DARK_GREY,
            BLACK,
        ]
        index = min(int(np.log10(mass)), len(colors) - 1)
        return colors[index]

    def mass_to_width(self, mass):
        return 1 + 0.25 * np.log10(mass)

    def mass_to_label_text(self, mass):
        return "{:,}\\,kg".format(int(mass))

class ClackFlashes(VGroup):
    CONFIG = {
        "flash_config": {
            "run_time": 0.5,
            "line_length": 0.1,
            "flash_radius": 0.2,
        },
        "start_up_time": 0,
        "min_time_between_flashes": 1 / 30,
    }

    def __init__(self, clack_data, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.flashes = []
        last_time = 0
        for location, time in clack_data:
            if (time - last_time) < self.CONFIG['min_time_between_flashes']:
                continue
            last_time = time
            flash = Flash(location, **self.CONFIG['flash_config'])
            flash.begin()
            for sm in flash.mobject.family_members_with_points():
                if isinstance(sm, VMobject):
                    sm.set_stroke(YELLOW, 3)
                    sm.set_stroke(WHITE, 6, 0.5, background=True)
            flash.start_time = time
            flash.end_time = time + flash.run_time
            self.flashes.append(flash)

        self.time = 0
        # self.add_updater(lambda m: m.update(dt))
        self.add_updater(self.update)

    def update(self, dt):
        time = self.time
        self.time += dt
        for flash in self.flashes:
            if flash.start_time < time < flash.end_time:
                if flash.mobject not in self.submobjects:
                    self.add(flash.mobject)
                flash.update(
                    (time - flash.start_time) / flash.run_time
                )
            else:
                if flash.mobject in self.submobjects:
                    self.remove(flash.mobject)


class PositionPhaseSpaceScene(Scene):
    CONFIG = {
        "rescale_coordinates": True,
        "wall_x": -6,
        "wall_config": {
            "height": 1.6,
            "tick_spacing": 0.35,
            "tick_length": 0.2,
        },
        "wall_height": 1.5,
        "floor_y": -3.5,
        "block1_config": {
            "mass": 10,
            "distance": 9,
            "velocity": -1,
            "width": 1.6,
        },
        "block2_config": {
            "mass": 1,
            "distance": 4,
        },
        "axes_config": {
            "x_min": -0.5,
            "x_max": 31,
            "y_min": -0.5,
            "y_max": 10.5,
            "x_axis_config": {
                "unit_size": 0.4,
                "tick_frequency": 2,
            },
            "y_axis_config": {
                "unit_size": 0.4,
                "tick_frequency": 2,
            },
        },
        "axes_center": 5 * LEFT + 0.65 * DOWN,
        "ps_dot_config": {
            "fill_color": RED,
            "background_stroke_width": 1,
            "background_stroke_color": BLACK,
            "radius": 0.05,
        },
        "ps_d2_label_vect": RIGHT,
        "ps_x_line_config": {
            "color": GREEN,
            "stroke_width": 2,
        },
        "ps_y_line_config": {
            "color": RED,
            "stroke_width": 2,
        },
        "clack_sound": "clack",
        "mirror_line_class": Line,
        "mirror_line_style": {
            "stroke_color": WHITE,
            "stroke_width": 1,
        },
        "d1_eq_d2_line_color": MAROON_B,
        "d1_eq_d2_tex": "d1 = d2",
        "trajectory_style": {
            "stroke_color": YELLOW,
            "stroke_width": 2,
        },
        "ps_velocity_vector_length": 0.75,
        "ps_velocity_vector_config": {
            "color": PINK,
            "rectangular_stem_width": 0.025,
            "tip_length": 0.15,
        },
        "block_velocity_vector_length_multiple": 2,
        "block_velocity_vector_config": {
            "color": PINK,
        },
    }

    def setup(self):
        self.total_sliding_time = 0
        self.all_items = [
            self.get_floor(),
            self.get_wall(),
            self.get_blocks(),
            self.get_axes(),
            self.get_phase_space_point(),
            self.get_phase_space_x_line(),
            self.get_phase_space_y_line(),
            self.get_phase_space_dot(),
            self.get_phase_space_d1_label(),
            self.get_phase_space_d2_label(),
            self.get_d1_brace(),
            self.get_d2_brace(),
            self.get_d1_label(),
            self.get_d2_label(),
            self.get_d1_eq_d2_line(),
            self.get_d1_eq_d2_label(),
            self.get_d2_eq_w2_line(),
            self.get_d2_eq_w2_label(),
        ]

    def get_floor_wall_corner(self):
        return self.CONFIG['wall_x'] * RIGHT + self.CONFIG['floor_y'] * UP

    def get_mass_ratio(self):
        return op.truediv(
            self.block1.mass,
            self.block2.mass,
        )

    def d1_to_x(self, d1):
        if self.CONFIG['rescale_coordinates']:
            d1 *= np.sqrt(self.block1.mass)
        return d1

    def d2_to_y(self, d2):
        if self.CONFIG['rescale_coordinates']:
            d2 *= np.sqrt(self.block2.mass)
        return d2

    def ds_to_point(self, d1, d2):
        return self.axes.coords_to_point(
            self.d1_to_x(d1), self.d2_to_y(d2),
        )

    def point_to_ds(self, point):
        x, y = self.axes.point_to_coords(point)
        if self.CONFIG['rescale_coordinates']:
            x /= np.sqrt(self.block1.mass)
            y /= np.sqrt(self.block2.mass)
        return (x, y)

    def get_d1(self):
        return self.get_ds()[0]

    def get_d2(self):
        return self.get_ds()[1]

    def get_ds(self):
        return self.point_to_ds(self.ps_point.get_location())

    # Relevant for sliding
    def tie_blocks_to_ps_point(self):
        def update_blocks(blocks):
            d1, d2 = self.point_to_ds(self.ps_point.get_location())
            b1, b2 = blocks
            corner = self.get_floor_wall_corner()
            b1.move_to(corner + d1 * RIGHT, DL)
            b2.move_to(corner + d2 * RIGHT, DR)
        self.blocks.add_updater(update_blocks)

    def time_to_ds(self, time):
        # Deals in its own phase space, different
        # from the one displayed
        m1 = self.block1.mass
        m2 = self.block2.mass
        v1 = self.block1.velocity
        start_d1 = self.CONFIG['block1_config']["distance"]
        start_d2 = self.CONFIG['block2_config']["distance"]
        w2 = self.block2.width
        start_d2 += w2
        ps_speed = np.sqrt(m1) * abs(v1)
        theta = np.arctan(np.sqrt(m2 / m1))

        def ds_to_ps_point(d1, d2):
            return np.array([
                d1 * np.sqrt(m1),
                d2 * np.sqrt(m2),
                0
            ])

        def ps_point_to_ds(point):
            return (
                point[0] / np.sqrt(m1),
                point[1] / np.sqrt(m2),
            )

        ps_point = ds_to_ps_point(start_d1, start_d2)
        wedge_corner = ds_to_ps_point(w2, w2)
        ps_point -= wedge_corner
        # Pass into the mirror worlds
        ps_point += time * ps_speed * LEFT
        # Reflect back to the real world
        angle = angle_of_vector(ps_point)
        n = int(angle / theta)
        if n % 2 == 0:
            ps_point = rotate_vector(ps_point, -n * theta)
        else:
            ps_point = rotate_vector(
                ps_point,
                -(n + 1) * theta,
            )
            ps_point[1] = abs(ps_point[1])
        ps_point += wedge_corner
        return ps_point_to_ds(ps_point)

    def get_clack_data(self):
        # Copying from time_to_ds.  Not great, but
        # maybe I'll factor things out properly later.
        m1 = self.block1.mass
        m2 = self.block2.mass
        v1 = self.block1.velocity
        w2 = self.block2.get_width()
        h2 = self.block2.get_height()
        start_d1, start_d2 = self.get_ds()
        ps_speed = np.sqrt(m1) * abs(v1)
        theta = np.arctan(np.sqrt(m2 / m1))

        def ds_to_ps_point(d1, d2):
            return np.array([
                d1 * np.sqrt(m1),
                d2 * np.sqrt(m2),
                0
            ])

        def ps_point_to_ds(point):
            return (
                point[0] / np.sqrt(m1),
                point[1] / np.sqrt(m2),
            )

        ps_point = ds_to_ps_point(start_d1, start_d2)
        wedge_corner = ds_to_ps_point(w2, w2)
        ps_point -= wedge_corner
        y = ps_point[1]

        clack_data = []
        for k in range(1, int(PI / theta) + 1):
            clack_ps_point = np.array([
                y / np.tan(k * theta), y, 0
            ])
            time = np.linalg.norm(ps_point - clack_ps_point) / ps_speed
            reflected_point = rotate_vector(
                clack_ps_point,
                -2 * np.ceil((k - 1) / 2) * theta
            )
            d1, d2 = ps_point_to_ds(reflected_point + wedge_corner)
            loc1 = self.get_floor_wall_corner() + h2 * UP / 2 + d2 * RIGHT
            if k % 2 == 0:
                loc1 += w2 * LEFT
            loc2 = self.ds_to_point(d1, d2)
            clack_data.append((time, loc1, loc2))
        return clack_data

    def tie_ps_point_to_time_tracker(self):
        if not hasattr(self, "sliding_time_tracker"):
            self.sliding_time_tracker = self.get_time_tracker()

        def update_ps_point(p):
            time = self.sliding_time_tracker.get_value()
            ds = self.time_to_ds(time)
            p.move_to(self.ds_to_point(*ds))

        self.ps_point.add_updater(update_ps_point)
        self.add(self.sliding_time_tracker, self.ps_point)

    def add_clack_flashes(self):
        if hasattr(self, "flash_anims"):
            self.add(*self.flash_anims)
        else:
            clack_data = self.get_clack_data()
            self.clack_times = [
                time for (time, loc1, loc2) in clack_data
            ]
            self.block_flashes = ClackFlashes([
                (loc1, time)
                for (time, loc1, loc2) in clack_data
            ])
            self.ps_flashes = ClackFlashes([
                (loc2, time)
                for (time, loc1, loc2) in clack_data
            ])
            self.flash_anims = [self.block_flashes, self.ps_flashes]
            for anim in self.flash_anims:
                anim.get_time = self.sliding_time_tracker.get_value
            self.add(*self.flash_anims)

    def get_continually_building_trajectory(self):
        trajectory = VMobject()
        self.trajectory = trajectory
        trajectory.set_style(**self.CONFIG['trajectory_style'])

        def get_point():
            return np.array(self.ps_point.get_location())

        points = [get_point(), get_point()]
        trajectory.set_points_as_corners(points)
        epsilon = 0.001

        def update_trajectory(trajectory):
            new_point = get_point()
            p1, p2 = trajectory.get_anchors()[-2:]
            angle = angle_between_vectors(
                p2 - p1,
                new_point - p2,
            )
            if angle > epsilon:
                points.append(new_point)
            else:
                points[-1] = new_point
            trajectory.set_points_as_corners(points)

        trajectory.add_updater(update_trajectory)
        return trajectory

    def begin_sliding(self, show_trajectory=True):
        self.tie_ps_point_to_time_tracker()
        self.add_clack_flashes()
        if show_trajectory:
            if hasattr(self, "trajectory"):
                self.trajectory.resume_updating()
            else:
                self.add(self.get_continually_building_trajectory())

    def end_sliding(self):
        self.update_mobjects(dt=0)
        self.ps_point.clear_updaters()
        if hasattr(self, "sliding_time_tracker"):
            self.remove(self.sliding_time_tracker)
        if hasattr(self, "flash_anims"):
            self.remove(*self.flash_anims)
        if hasattr(self, "trajectory"):
            self.trajectory.suspend_updating()
        old_total_sliding_time = self.total_sliding_time
        new_total_sliding_time = self.sliding_time_tracker.get_value()
        self.total_sliding_time = new_total_sliding_time
        

    def slide(self, time, stop_condition=None):
        self.begin_sliding()
        self.wait(time, stop_condition)
        self.end_sliding()

    def slide_until(self, stop_condition, max_time=60):
        self.slide(max_time, stop_condition=stop_condition)

    def get_ps_point_change_anim(self, d1, d2, **added_kwargs):
        b1 = self.block1
        ps_speed = np.sqrt(b1.mass) * abs(b1.velocity)
        curr_d1, curr_d2 = self.get_ds()
        distance = np.linalg.norm([curr_d1 - d1, curr_d2 - d2])

        # Default
        kwargs = {
            "run_time": (distance / ps_speed),
            "rate_func": linear,
        }
        kwargs.update(added_kwargs)
        return ApplyMethod(
            self.ps_point.move_to,
            self.ds_to_point(d1, d2),
            **kwargs
        )

    # Mobject getters
    def get_floor(self):
        floor = self.floor = Line(
            self.CONFIG['wall_x'] * RIGHT,
            config['frame_width'] * RIGHT / 2,
            stroke_color=WHITE,
            stroke_width=3,
        )
        floor.move_to(self.get_floor_wall_corner(), LEFT)
        return floor

    def get_wall(self):
        wall = self.wall = Wall(**self.CONFIG['wall_config'])
        wall.move_to(self.get_floor_wall_corner(), DR)
        return wall

    def get_blocks(self):
        blocks = self.blocks = VGroup()
        for n in [1, 2]:
            config = getattr(self, "block{}_config".format(n))
            block = Block(**config)
            block.move_to(self.get_floor_wall_corner(), DL)
            block.shift(config["distance"] * RIGHT)
            block.label.move_to(block)
            block.label.set_fill(BLACK)
            block.label.set_stroke(WHITE, 1, background=True)
            self.blocks.add(block)
        self.block1, self.block2 = blocks
        return blocks

    def get_axes(self):
        axes = self.axes = Axes(**self.CONFIG['axes_config'])
        axes.set_stroke(LIGHT_GREY, 2)
        axes.shift(
            self.CONFIG['axes_center'] - axes.coords_to_point(0, 0)
        )
        axes.labels = self.get_axes_labels(axes)
        axes.add(axes.labels)
        axes.added_lines = self.get_added_axes_lines(axes)
        axes.add(axes.added_lines)
        return axes

    def get_added_axes_lines(self, axes):
        c2p = axes.coords_to_point
        x_mult = y_mult = 1
        if self.CONFIG['rescale_coordinates']:
            x_mult = np.sqrt(self.block1.mass)
            y_mult = np.sqrt(self.block2.mass)
        y_lines = VGroup(*[
            Line(
                c2p(0, 0), c2p(0, axes.y_max * y_mult + 1),
            ).move_to(c2p(x, 0), DOWN)
            for x in np.arange(0, axes.x_max) * x_mult
        ])
        x_lines = VGroup(*[
            Line(
                c2p(0, 0), c2p(axes.x_max * x_mult, 0),
            ).move_to(c2p(0, y), LEFT)
            for y in np.arange(0, axes.y_max) * y_mult
        ])
        line_groups = VGroup(x_lines, y_lines)
        for lines in line_groups:
            lines.set_stroke(BLUE, 1, 0.5)
            lines[1::2].set_stroke(width=0.5, opacity=0.25)
        return line_groups

    def get_axes_labels(self, axes, with_sqrts=None):
        if with_sqrts is None:
            with_sqrts = self.CONFIG['rescale_coordinates']
        x_label = MathTex("x", "=", "d_1")
        y_label = MathTex("y", "=", "d_2")
        labels = VGroup(x_label, y_label)
        if with_sqrts:
            additions = map(MathTex, [
                "\\sqrt{m_1}", "\\sqrt{m_2}"
            ])
            for label, addition in zip(labels, additions):
                addition.move_to(label[2], DL)
                label[2].next_to(
                    addition, RIGHT, SMALL_BUFF,
                    aligned_edge=DOWN
                )
                addition[2:].set_color(BLUE)
                label.submobjects.insert(2, addition)
        x_label.next_to(axes.x_axis.get_right(), DL, MED_SMALL_BUFF)
        y_label.next_to(axes.y_axis.get_top(), DR, MED_SMALL_BUFF)
        for label in labels:
            label.shift_onto_screen()
        return labels

    def get_phase_space_point(self):
        ps_point = self.ps_point = VectorizedPoint()   # aca esta
        ps_point.move_to(self.ds_to_point(
            self.block1.distance,
            self.block2.distance + self.block2.width
        ))
        self.tie_blocks_to_ps_point()
        return ps_point

    def get_phase_space_x_line(self):
        def get_x_line():
            origin = self.axes.coords_to_point(0, 0)
            point = self.ps_point.get_location()
            y_axis_point = np.array(origin)
            y_axis_point[1] = point[1]
            return DashedLine(
                y_axis_point, point,
                **self.CONFIG['ps_x_line_config'],
            )
        self.x_line = always_redraw(get_x_line)
        return self.x_line

    def get_phase_space_y_line(self):
        def get_y_line():
            origin = self.axes.coords_to_point(0, 0)
            point = self.ps_point.get_location()
            x_axis_point = np.array(origin)
            x_axis_point[0] = point[0]
            return DashedLine(
                x_axis_point, point,
                **self.CONFIG['ps_y_line_config'],
            )
        self.y_line = always_redraw(get_y_line)
        return self.y_line

    def get_phase_space_dot(self):
        self.ps_dot = ps_dot = Dot(**self.CONFIG['ps_dot_config'])
        ps_dot.add_updater(lambda m: m.move_to(self.ps_point))
        return ps_dot

    def get_d_label(self, n, get_d):
        label = VGroup(
            MathTex("d_{}".format(n), "="),
            DecimalNumber(),
        )
        color = GREEN if n == 1 else RED
        label[0].set_color_by_tex("d_", color)
        label.scale(0.7)
        label.set_stroke(BLACK, 3, background=True)

        def update_value(label):
            lhs, rhs = label
            rhs.set_value(get_d())
            rhs.next_to(
                lhs, RIGHT, SMALL_BUFF,
                aligned_edge=DOWN,
            )
        label.add_updater(update_value)
        return label

    def get_phase_space_d_label(self, n, get_d, line, vect):
        label = self.get_d_label(n, get_d)
        label.add_updater(
            lambda m: m.next_to(line, vect, SMALL_BUFF)
        )
        return label

    def get_phase_space_d1_label(self):
        self.ps_d1_label = self.get_phase_space_d_label(
            1, self.get_d1, self.x_line, UP,
        )
        return self.ps_d1_label

    def get_phase_space_d2_label(self):
        self.ps_d2_label = self.get_phase_space_d_label(
            2, self.get_d2, self.y_line,
            self.CONFIG['ps_d2_label_vect'],
        )
        return self.ps_d2_label

    def get_d_brace(self, get_right_point):
        line = Line(LEFT, RIGHT).set_width(6)

        def get_brace():
            right_point = get_right_point()
            left_point = np.array(right_point)
            left_point[0] = self.CONFIG['wall_x']
            line.put_start_and_end_on(left_point, right_point)
            return Brace(line, UP, buff=SMALL_BUFF)

        brace = always_redraw(get_brace)
        return brace

    def get_d1_brace(self):
        self.d1_brace = self.get_d_brace(
            lambda: self.block1.get_corner(UL)
        )
        return self.d1_brace

    def get_d2_brace(self):
        self.d2_brace = self.get_d_brace(
            lambda: self.block2.get_corner(UR)
        )
        # self.flip_brace_nip()
        return self.d2_brace

    def flip_brace_nip(self, brace):
        nip_index = (len(brace) // 2) - 1
        nip = brace[nip_index:nip_index + 2]
        rect = brace[nip_index - 1]
        center = rect.get_center()
        center[0] = nip.get_center()[0]
        nip.rotate(PI, about_point=center)

    def get_brace_d_label(self, n, get_d, brace, vect, buff):
        label = self.get_d_label(n, get_d)
        label.add_updater(
            lambda m: m.next_to(brace, vect, buff)
        )
        return label

    def get_d1_label(self):
        self.d1_label = self.get_brace_d_label(
            1, self.get_d1, self.d1_brace, UP, SMALL_BUFF,
        )
        return self.d1_label

    def get_d2_label(self):
        self.d2_label = self.get_brace_d_label(
            2, self.get_d2, self.d2_brace, UP, 0
        )
        return self.d2_label

    def get_d1_eq_d2_line(self):
        start = self.ds_to_point(0, 0)
        end = self.ds_to_point(15, 15)
        line = self.d1_eq_d2_line = self.CONFIG['mirror_line_class'](start, end)
        line.set_style(**self.CONFIG['mirror_line_style'])
        line.set_color(self.CONFIG['d1_eq_d2_line_color'])
        return self.d1_eq_d2_line

    def get_d1_eq_d2_label(self):
        label = MathTex(self.CONFIG['d1_eq_d2_tex'])
        label.scale(0.75)
        line = self.d1_eq_d2_line
        point = interpolate(
            line.get_start(), line.get_end(),
            0.7,
        )
        label.next_to(point, DR, SMALL_BUFF)
        label.match_color(line)
        label.set_stroke(BLACK, 5, background=True)
        self.d1_eq_d2_label = label
        return label

    def get_d2_eq_w2_line(self):
        w2 = self.block2.width
        start = self.ds_to_point(0, w2)
        end = np.array(start)
        end[0] = config['frame_width'] / 2
        self.d2_eq_w2_line = self.CONFIG['mirror_line_class'](start, end)
        self.d2_eq_w2_line.set_style(**self.CONFIG['mirror_line_style'])
        return self.d2_eq_w2_line

    def get_d2_eq_w2_label(self):
        label = MathTex("d2 = \\text{block width}")
        label.scale(0.75)
        label.next_to(self.d2_eq_w2_line, UP, SMALL_BUFF)
        label.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        self.d2_eq_w2_label = label
        return label

    def get_time_tracker(self, time=0):
        time_tracker = self.time_tracker = ValueTracker(time)
        time_tracker.add_updater(
            lambda m, dt: m.increment_value(dt)
        )
        return time_tracker

    # Things associated with velocity
    def get_ps_velocity_vector(self, trajectory):
        vector = Vector(
            self.CONFIG['ps_velocity_vector_length'] * LEFT,
            **self.CONFIG['ps_velocity_vector_config'],
        )

        def update_vector(v):
            anchors = trajectory.get_anchors()
            index = len(anchors) - 2
            vect = np.array(ORIGIN)
            while np.linalg.norm(vect) == 0 and index > 0:
                p0, p1 = anchors[index:index + 2]
                vect = p1 - p0
                index -= 1
            angle = angle_of_vector(vect)
            point = self.ps_point.get_location()
            v.set_angle(angle)
            v.shift(point - v.get_start())
        vector.add_updater(update_vector)
        self.ps_velocity_vector = vector
        return vector

    def get_block_velocity_vectors(self, ps_vect):
        blocks = self.blocks
        vectors = VGroup(*[
            Vector(LEFT, **self.CONFIG['block_velocity_vector_config'])
            for x in range(2)
        ])
        # TODO: Put in config
        vectors[0].set_color(GREEN)
        vectors[1].set_color(RED)

        def update_vectors(vs):
            v_2d = ps_vect.get_vector()[:2]
            v_2d *= self.CONFIG['block_velocity_vector_length_multiple']
            for v, coord, block in zip(vs, v_2d, blocks):
                v.put_start_and_end_on(ORIGIN, coord * RIGHT)
                start = block.get_edge_center(v.get_vector())
                v.shift(start)
        vectors.add_updater(update_vectors)

        self.block_velocity_vectors = vectors
        return vectors


class IntroducePositionPhaseSpace(PositionPhaseSpaceScene):
    CONFIG = {
        "rescale_coordinates": False,
        "d1_eq_d2_tex": "x = y",
        "block1_config": {
            "velocity": 1.5,
        },
        "slide_wait_time": 12,
    }

    def setup(self):
        super().setup()
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
        )

    def construct(self):
        self.show_coordinates()
        self.show_xy_line()
        self.let_process_play_out()
        self.show_w2_line()

    def show_coordinates(self):
        ps_point = self.ps_point
        axes = self.axes

        self.play(Write(axes.added_lines))
        self.play(FadeIn(self.ps_dot, scale_factor=10))
        self.play(
            Create(self.x_line),
            GrowFromPoint(
                self.d1_brace,
                self.d1_brace.get_left(),
            ),
            Indicate(axes.labels[0]),
        )
        self.play(
            FadeIn(self.ps_d1_label),
            FadeIn(self.d1_label),
        )
        self.play(ps_point.shift, 0.5 * LEFT)
        self.play(ps_point.shift, 0.5 * RIGHT)
        self.wait()
        self.play(
            Create(self.y_line),
            GrowFromPoint(
                self.d2_brace,
                self.d2_brace.get_left(),
            ),
            Indicate(axes.labels[1]),
        )
        self.play(
            FadeIn(self.ps_d2_label),
            FadeIn(self.d2_label),
        )
        self.play(ps_point.shift, 0.5 * UP)
        self.play(ps_point.shift, 0.5 * DOWN)
        self.wait()
        self.play(Rotating(
            ps_point,
            about_point=ps_point.get_location() + 0.5 * RIGHT,
            run_time=3,
            rate_func=smooth,
        ))
        self.wait()

    def show_xy_line(self):
        ps_point = self.ps_point
        ps_point.save_state()
        d1, d2 = self.point_to_ds(ps_point.get_location())

        xy_line = self.d1_eq_d2_line
        xy_label = self.d1_eq_d2_label

        self.play(
            Create(xy_line),
            Write(xy_label),
        )
        self.play(
            ps_point.move_to, self.ds_to_point(d2, d2),
            run_time=3
        )
        self.wait()
        for d in [3, 7]:
            self.play(
                ps_point.move_to, self.ds_to_point(d, d),
                run_time=2
            )
            self.wait()
        self.play(ps_point.restore)
        self.wait()

    def let_process_play_out(self):
        self.begin_sliding()
        sliding_trajectory = self.get_continually_building_trajectory()
        self.add(sliding_trajectory, self.ps_dot)
        self.wait(self.slide_wait_time)

    def show_w2_line(self):
        line = self.d2_eq_w2_line
        label = self.d2_eq_w2_label

        self.play(Create(line))
        self.play(FadeIn(label))
        self.wait(self.slide_wait_time)
        self.end_sliding()
        self.wait(self.slide_wait_time)