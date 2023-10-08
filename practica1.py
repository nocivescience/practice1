from manim import *
# triangle=Triangle()
# if isinstance(triangle, VMobject):
#     print("triangle is a VMobject")
# else:
#     print("triangle is not a VMobject") 
class ClassOne:
    def __init__(self) -> None:
        pass
class ClassTwo(ClassOne):
    def __init__(self) -> None:
        pass
class1=ClassOne()
class2=ClassTwo()
print(class1==class2)