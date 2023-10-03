from manim import *
class Pendulum(VGroup):
    configuracion = {
        'mass_config': {
            'radius': 0.6,
            'color': RED,
            'fill_opacity': 1,
        },
        'string_config': {
            'color': WHITE,
            'stroke_width': 3,
        },
        'theta_max': PI/4,
        'length': 4,
        'theta_start': None,
        'theta_offset': 0,
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self,**kwargs)
        if self.configuracion['theta_start'] is None:
            self.configuracion['theta_start'] = self.configuracion['theta_max']
        self.mass = self.get_mass()
        self.string = self.get_string()
        self.rotate(self.configuracion['theta_start'])
        self.add_updater(lambda t: self.updatting_mass())
        self.add(self.mass, self.string)
    def get_string(self):
        return Line(ORIGIN, UP, **self.configuracion['string_config']).set_z_index(-1)
    def get_mass(self):
        return Dot(**self.configuracion['mass_config'])
    def updatting_mass(self):
        self.mass.move_to(self.string.get_end())
    # def restore_string(self):
        # self.string.restore()
    def rotate(self,angle):
        self.string.rotate(angle, about_point=self.string.get_start())
class PendulumScene(Scene):
    configuracion2 = {
        'gravedad': 9.8,
        'dt_factor': 3,
        'total_time': 3,
    }
    def construct(self):
        pendulo = Pendulum()
        self.add(pendulo)
        self.play(Rotating(pendulo.string, radians=PI/2, about_point=pendulo.string.get_start(), rate_func=linear, run_time=2))
        self.wait()
        pendulo.add_updater(self.get_theta_func(pendulo))
        self.wait(self.configuracion2['total_time'])
    def get_theta_func(self,mob):
        func=lambda t: mob.configuracion['theta_max']*np.sin(t* np.sqrt(self.configuracion2['gravedad']/mob.configuracion['length']))
        def update_theta(mob, dt):
            mob.configuracion['theta_offset'] += dt*self.configuracion2['dt_factor']
            mob.theta = func(mob.configuracion['theta_offset'])
            # mob.restore_string()
            mob.rotate(mob.theta)
        return update_theta
