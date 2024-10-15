import numpy as np
from abc import ABC, abstractmethod

class Sphere(ABC):
    def __init__(self, position, velocity, radius, particle_type, mass):
        self.position = np.array(position, dtype=np.float32)  
        self.velocity = np.array(velocity, dtype=np.float32) 
        self.radius = radius
        self.particle_type = particle_type
        self.mass = mass

    @abstractmethod
    def apply_force(self, force, dt):
        pass

    def update(self, dt, gravity=9.81):
        self.position += self.velocity * dt
        self.velocity[1] -= gravity * dt

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Pérdida de energía al rebotar

    def check_collision(self, other):
        distance = np.linalg.norm(self.position - other.position)
        return distance < self.radius + other.radius

    def resolve_collision(self, other):
        normal = other.position - self.position
        normal = normal / np.linalg.norm(normal)

        relative_velocity = self.velocity - other.velocity
        velocity_along_normal = np.dot(relative_velocity, normal)

        if velocity_along_normal > 0:
            return  # No hay colisión si están alejándose

        restitution = 0.9
        j = -(1 + restitution) * velocity_along_normal
        j /= (1 / self.mass + 1 / other.mass)

        impulse = j * normal
        self.velocity -= impulse / self.mass
        other.velocity += impulse / other.mass

        self.handle_particle_interaction(other)

    @abstractmethod
    def handle_particle_interaction(self, other):
        pass


class Electron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.1, particle_type='electron', mass=9.11e-31)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        if other.particle_type == 'proton':
            # Atraer a protones
            self.velocity += 0.1 * (other.position - self.position) / np.linalg.norm(other.position - self.position)
        elif other.particle_type == 'photon':
            # Interacción con fotones
            self.velocity *= 0.9  # Pérdida de energía al interactuar con fotones


class Proton(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='proton', mass=1.67e-27)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        if other.particle_type == 'electron':
            # Reacción a la colisión con electrones
            self.velocity += 0.05 * (self.position - other.position) / np.linalg.norm(self.position - other.position)


class Neutron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='neutron', mass=1.67e-27)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        # Interacciones específicas del neutrón pueden ser definidas aquí
        pass


class Photon(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.05, particle_type='photon', mass=0)

    def apply_force(self, force, dt):
        # Fotones no aplican fuerzas ya que tienen masa cero
        pass

    def update(self, dt):
        self.position += self.velocity * dt  # Viaja a la velocidad de la luz

    def handle_particle_interaction(self, other):
        # Puede interactuar con otras partículas, posiblemente transferiendo energía
        pass


class HiggsBoson(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.3, particle_type='Higgs Boson', mass=2.2e-25)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        # Interacciones específicas del bosón de Higgs
        pass


class FluidSphere(Sphere):
    def __init__(self, position, velocity, radius):
        super().__init__(position, velocity, radius, particle_type='fluid', mass=1.0)

    def apply_force(self, force, dt):
        # Simulación de fuerzas en un fluido
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def deform(self):
        # Método para simular la deformación de la esfera cuando actúa como un fluido
        self.radius *= 1.1

    def simulate_fluid_behavior(self, other):
        distance = np.linalg.norm(self.position - other.position)
        if distance < self.radius + other.radius:
            self.radius = (self.radius + other.radius) / 2
            self.velocity = (self.velocity + other.velocity) / 2

    def handle_particle_interaction(self, other):
        # Lógica específica de interacción de fluidos
        pass


# Sistema de Fuerzas (Ejemplo simplificado)
class Force:
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = np.array(direction) / np.linalg.norm(direction)

    def apply(self, particle,dt):
        force_vector = self.direction * self.magnitude
        particle.apply_force(force_vector, dt)


