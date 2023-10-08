from manim import *
class Cuadro(Triangle):
    def __init__(self, **kwargs):
        Triangle.__init__(self, **kwargs)
class CuadroScene(Scene):
    def setup1(self):
        self.all__items=[
            self.get_cuadro(),
        ]
    def get_cuadro(self):
        self.cuadro=Cuadro(color=RED)
        return self.cuadro
class RepeticionScene(CuadroScene):
    def setup(self):
        super().setup1()
        self.play(Create(self.cuadro))
        self.wait()