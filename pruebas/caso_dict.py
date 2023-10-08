from manim import *
class Block(Square):
    configuracion={
        'tick_spacing': .5,
        'tick_length': .25,
        'tick_style': {
            'stroke_width': 1,
            'stroke_color': WHITE,
        },
    }
    def __init__(self, **kwargs):
        Square.__init__(self, **kwargs)
class PruebaScene(Scene):
    configuracion={
        'propiedad': 4,
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
    }
    def construct(self):
        parte1= Triangle().scale(2)
        parte2= 3
        parte1.parte2=parte2
        return getattr(parte1, 'parte2')
        # return [self.configuracion['block{}_config'.format(n)] for n in [1,2]]
        # return Block().configuracion['tick_spacing']
print(PruebaScene().construct())