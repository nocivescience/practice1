from manim import *
class Poligono(RegularPolygon):
    def __init__(self,n=4, **kwargs):
        RegularPolygon.__init__(self, **kwargs)
        self.n=n
class PoligonoScene(Scene):
    def construct(self):
        poligono=Poligono(n=12)
        self.play(Create(poligono))
        self.wait()