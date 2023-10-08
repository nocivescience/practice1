from manim import *
import itertools as it
class CreationDestructionMobject(VMobject):
    configure={
        'use_copy': False,
        'start_time': 0,
        'frequency': .25,
        'max_ratio_shown': .3,
    }
    def __init__(self, template, **kwargs):
        VMobject.__init__(self, **kwargs)
        if self.configure['use_copy']:
            self.ghost_mob=template.copy().fade(1)
            self.add(self.ghost_mob)
        else:
            self.ghost_mob=template
        self.shown_mob=template.copy()
        self.shown_mob.clear_updaters()
        self.add(self.shown_mob)
        self.total_time= self.configure['start_time']
        def update(mob,dt):
            mob.total_time+=dt
            period=1/mob.configure['frequency']
            unsmooth_alpha=(mob.total_time%period)/period
            smooth_alpha=bezier([0,0,1,1])(unsmooth_alpha)
            mrs=mob.configure['max_ratio_shown']
            mob.shown_mob.pointwise_become_partial(
                mob.ghost_mob,
                max(interpolate(-mrs,1,smooth_alpha),np.random.random()),
                min(interpolate(0, mrs+1,smooth_alpha),1-np.random.random()),
            )
        self.add_updater(update)
class Eddy(Mobject):
    configure={
        'cd_mob_config': {
            'frequency': .2,
            'max_ratio_shown': .3,
        },
        'colors': [RED, GREEN, BLUE, YELLOW],
        'n_cds': 50,
    }
    def __init__(self, **kwargs): #lo tenia como __add__
        Mobject.__init__(self, **kwargs)
        self.colors=it.cycle(self.configure['colors'])
        self.radios=np.linspace(1,3,self.configure['n_cds'])
        lines=self.get_lines()
        self.add(*[
            CreationDestructionMobject(
                line,
                # **self.configure['cd_mob_config'],
            )
            for line in lines
        ])
        self.randomize_items()
    def randomize_items(self):
        for submob in self.submobjects:
            t=self.configure['cd_mob_config']['frequency']*np.random.random()
            self.configure['cd_mob_config']['start_time']=t
    def get_lines(self):
        return VGroup(*[
            self.get_line(t*np.random.random())
            for t in self.radios
        ])
    def get_line(self,l=None):
        return RegularPolygon(n=6,color=next(self.colors)).scale(l)
class CreateDestructionScene(Scene):
    def construct(self):
        mobjeto = Eddy()
        self.add(mobjeto)
        self.wait(14)