from manim import *
import itertools as it
class Wall(Line):
    configuracion={
        'tick_spacing': .1,
        'tick_length': .1,
        'tick_style': {
            'stroke_width': 2,
            'stroke_color': WHITE,
        },
    }
    def __init__(self, height, **kwargs):
        Line.__init__(self, ORIGIN, UP*height, **kwargs)
        self.height=height
        self.ticks= self.get_ticks()
        self.add(self.ticks)
    def get_ticks(self):
        n_lines= int(self.height/self.configuracion['tick_spacing'])
        lines=VGroup(*[
            Line(ORIGIN, self.configuracion['tick_length']*DR,**self.configuracion['tick_style']).shift(
                n*self.configuracion['tick_spacing']*UP
            ) for n in range(n_lines)
        ])  
        lines.move_to(self,DR)
        return lines
class Block(Square):
    configuracion={
        'mass': 1,
        'velocity': 0,
        'width': None,
        'label_text': None,
        'label_scale_value': .8,
        'fill_opacity': 1,
        'stroke_width': 2,
        'stroke_color': BLUE_C,
        'fill_color': None,
        'sheen_direction': UL,
    }
    def __init__(self, **kwargs):
        if self.configuracion['fill_color'] is None:
            self.configuracion['width']=self.mass_to_width(self.configuracion['mass'])
        if self.configuracion['label_text'] is None:
            self.configuracion['label_text']=self.mass_to_label_text(self.configuracion['mass'])
        if 'width' in kwargs:
            kwargs.pop('width')
        Square.__init__(self, side_length=self.configuracion['width'], **kwargs)
        self.label=self.get_label()
        self.add(self.label)
    def get_label(self):
        label=Tex(self.configuracion['label_text'])
        label.scale(self.configuracion['label_scale_value'])
        label.next_to(self, UP, buff=SMALL_BUFF)
        return label
    def get_points_defining_boundaries(self):
        return self.points
    def mass_to_color(self, mass):
        colors=[GREEN, YELLOW, RED, PURPLE_A, PURPLE_B, TEAL, BLUE, GREY]
        index= np.min(np.log(mass), len(colors)-1)
        return colors[index]
    def mass_to_width(self, mass):
        return 1+.25*np.log(mass)
    def mass_to_label_text(self, mass):
        return "{:,}\\, kg".format(int(mass))
class ClackFlashes(VGroup):
    configuracion={
        'flash_config': {
            'run_time': .5,
            'line_length': .1,
            'flash_radius': .2,
            'start_up_time': 0,
            'min_time_between_flashes': 1/30,
        },
    }
    def __init__(self, clack_data, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.flashes=[]
        last_time=0
        for location, time in clack_data:
            if (time-last_time)<self.configuracion['min_time_between_flash']:
                continue
            last_time=time
            flash=Flash(location, **self.configuracion['flash_config'])
            flash.begin()
            for sm in flash.mobject.family_members_with_points():
                if isinstance(sm, VMobject):
                    sm.set_stroke(opacity=1, color=YELLOW, background=True)
            flash_start_time=time
            flash_end_time=time+self.configuracion['flash_config']['run_time']
            self.flashes.append(flash)
        self.time=0
        self.add_updater(lambda m, dt: m.update(dt))
    def update(self, dt):
        self.time+=dt
        for flash in self.flashes:
            if (flash.start_time<self.time) and (flash.end_time>self.time):
                if  flash.mobject not in self.submobjects:
                    self.add(flash.mobject)
            else:
                if flash.mobject in self.submobjects:
                    self.remove(flash.mobject)
class BlockScene(Scene):
    configuracion={

    }
    def setup(self):
        wall=Wall(3)
        block=Block()
        self.play(Create(wall), Create(block))
        self.wait()
class PositionPhaseSpaceScene(Scene):
    configuracion={

    }
    def setup(self):
        self.total_sliding_time=0
        self.all_items=[
            self.get_wall(),
            self.get_block(),
        ]
    def get_wall(self):
        self.wall=Wall(3)
        return self.wall
    def get_block(self):
        self.block=Block()
        return self.block
class IntroducePositionPhaseSpace(PositionPhaseSpaceScene):
    configuracion={

    }
    def setup(self):
        super().setup()
        self.add(self.wall, self.block)
        self.wait()
    def construct(self):
        pass
    def show_coordinates(self):
        pass