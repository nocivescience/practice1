from manim import *
class FourierCirclesScene(ZoomedScene):
    def setup(self):
        ZoomedScene.setup(self)
class FourierCirclesScene1(FourierCirclesScene):
    configuracion={
        'n_vectors': 5,
        'center_point': ORIGIN,
        'vector_config': {
            'buff': 0,
            'max_tip_length_to_length_ratio': 0.25,
            'tip_length': 0.25,
            'max_stroke_width_to_length_ratio': 10,
            'stroke_width': 1.6,
            'color': BLUE,
        },
        'slow_factor': 0.5,
    }
    def construct(self):
        self.vector_clock=ValueTracker(0)
        self.slow_factor_tracker=ValueTracker(self.configuracion['slow_factor'])
        self.activate_zooming(animate=True)
        self.add_vectors_circles_path()
        self.wait()
    def add_vectors_circles_path(self):
        path= self.get_path()
        coefficients=self.get_coefficients_on_path(path)
        vector1=self.get_rotating_vectors(coefficients)
        self.play(Create(path), run_time=2)
        self.play(Create(vector1), run_time=2)
        self.wait()
    def get_freqs(self):
        n=self.configuracion['n_vectors']
        all_freqs = list(range(n//2, -n//2, -1))
        all_freqs.sort(key=abs)
        return all_freqs
    def get_coefficients(self):
        return [
            complex(0) for _ in range(self.configuracion['n_vectors'])
        ]
    def get_path(self):
        text_mob=MathTex(r'\rm R')
        text_mob.set_height(5)
        path=text_mob.family_members_with_points()[0]
        return path
    def get_coefficients_on_path(self, path, n_samples=100, freqs=None):
        if freqs is None:
            freqs = self.get_freqs()
        dt=1/n_samples
        ts=np.arange(0,1+dt,dt)
        samples=np.array([path.point_from_proportion(t) for t in ts])
        samples-=self.configuracion['center_point']
        complex_samples= samples[:,0]+1j*samples[:,1]
        return [
            np.array([
                np.exp(-TAU*1j*freq*t)*cs for t,cs in zip(ts,complex_samples)
            ]).sum()*dt for freq in freqs
        ]
    def get_rotating_vector(self, coefficient, freq, center_func):
        vector=Vector(RIGHT, **self.configuracion['vector_config']).set_z_index(2)
        vector.scale(abs(coefficient))
        if abs(coefficient)==0:
            phase=0
        else:
            phase=np.log(coefficient).imag
        vector.rotate(phase, about_point=ORIGIN)
        vector.freq=freq
        vector.coefficient=coefficient
        vector.center_func=center_func
        vector.add_updater(self.update_vector)
        return vector
    def get_rotating_vectors(self, freqs=None, coefficients=None):
        vectors=VGroup()
        self.center_tracker = VectorizedPoint(self.configuracion['center_point'])
        if freqs is None:
            freqs=self.get_freqs()
        if coefficients is None:
            coefficients=self.get_coefficients()
        last_vector=None
        for freq, coefficient in zip(freqs, coefficients):
            if last_vector:
                center_func = last_vector.get_end
            else:
                center_func = self.center_tracker.get_location
            vector=self.get_rotating_vector(coefficient=coefficient, freq=freq, center_func=center_func)
            vectors.add(vector) 
            last_vector=vector
        return vectors
    def update_vector(self, vector, dt):
        time=self.vector_clock.get_value()
        coef=vector.coefficient
        freq=vector.freq
        phase=np.log(coef).imag
        vector.set_length(abs(coef))
        vector.set_angle(freq*time*TAU+phase)
        vector.shift(vector.center_func()-vector.get_start())
        return vector