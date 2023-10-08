from manim import *
class ClaseOne(Circle):
    configu={
        'color': RED,
        'length': 2,
    }
class ClaseTwo(Circle):
    configu={
        'color': BLUE,
        'length': 22,
    }
clase1=ClaseOne()
print(clase1.configu['length'])