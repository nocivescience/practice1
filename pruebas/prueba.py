from manim import *
class Prueba(Mobject):
    configuracion={
        'use_copy': True,
        'start_time': 0,
        'frequency': .25,
        'max_ratio_shown': .3,
    }
    pass
miprueba=Prueba()
if 'use_copy' in miprueba.__dict__:
    print("miprueba has use_copy")
else:
    print("miprueba has not use_copy")