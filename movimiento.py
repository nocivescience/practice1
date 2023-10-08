from manim import *
def get_path_angle(path, proportion, dx=.001):
    if proportion < 1:
        coord_i = path.point_from_proportion(proportion)
        coord_f = path.point_from_proportion(proportion+dx)
    else:
        coord_i = path.point_from_proportion(proportion-dx)
        coord_f = path.point_from_proportion(proportion)
    line=Line(coord_i,coord_f)
    angle=line.get_angle()
    return angle
class ShiftingPath(Animation):
    def __init__(self, mobject, path, **kwargs):
        Animation.__init__(self, mobject, **kwargs)
        assert(isinstance(path, VMobject))
        self.path = path
        self.mobject = mobject
    def interpolate_mobject(self, alpha):
        self.mobject.become(self.starting_mobject)
        self.mobject.move_to(self.path.point_from_proportion(alpha))
        angle=get_path_angle(self.path,alpha)
        self.mobject.rotate(angle,about_point=self.path.point_from_proportion(alpha))
class PendulumScene(Scene):
    def construct(self):
        path=VMobject()
        path.set_points_smoothly([
            [0,5,0],
            [1,1,0],
            [2,1,0],
            [3,0,0],
            [4,-7,0]
        ])
        path.center()
        path.set(height=config["frame_height"]-2)
        triangle=Triangle()
        triangle.move_to(path.get_start())
        self.play(Create(path), Create(triangle))
        self.play(ShiftingPath(triangle,path,run_time=5))
        self.wait()