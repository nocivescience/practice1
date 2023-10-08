from manim import *
numero=5
valor=ValueTracker(numero)
posicion= lambda: valor.get_value()
posicion2= valor.get_value
posicion3= valor.get_value() 
caso1= np.array([1,2,3])
caso11= VectorizedPoint(caso1)
print(caso11.get_location())
print(caso11.get_location()==caso1)