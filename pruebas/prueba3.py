from manim import *
class Path(VMobject):
    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.path=VMobject()
        self.path.set_points_as_corners([ORIGIN, RIGHT, UP])
        self.add(self.path)
class PathScene(Scene):
    def setup(self):
        self.components=[
            self.get_path(),
        ]
    def get_path(self):
        self.path=Path()
        return self.path
class PathAnimation(PathScene):
    def setup(self):
        super().setup()
    # def construct(self):
        self.play(Create(self.path))
        self.wait()