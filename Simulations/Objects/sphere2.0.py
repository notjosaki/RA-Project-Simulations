import numpy as np

class Sphere:
    def __init__(self, position, velocity, radius, particle_type):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.radius = radius
        self.particle_type = particle_type  # Tipo de partícula

    def update(self, dt, gravity=9.81):
        self.position += self.velocity * dt
        self.velocity[1] -= gravity * dt  # Gravedad variable

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Pérdida de energía al rebotar

    def apply_force(self, force, dt):
        # Aplica una fuerza a la esfera
        acceleration = force / self.radius  # Suponiendo masa proporcional al radio
        self.velocity += acceleration * dt

    def check_collision(self, other):
        distance = np.linalg.norm(self.position - other.position)
        return distance < self.radius + other.radius

    def resolve_collision(self, other):
        normal = other.position - self.position
        normal = normal / np.linalg.norm(normal)  # Normalizar la dirección

        relative_velocity = self.velocity - other.velocity
        velocity_along_normal = np.dot(relative_velocity, normal)

        if velocity_along_normal > 0:
            return  # No hay colisión si están alejándose

        restitution = 0.9  # Coeficiente de restitución
        j = -(1 + restitution) * velocity_along_normal
        j /= (1 / self.radius + 1 / other.radius)

        impulse = j * normal
        self.velocity -= impulse / self.radius
        other.velocity += impulse / other.radius

class Electron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.1, particle_type='electron')

    def update(self, dt):
        super().update(dt, gravity=0)  # Electrones no sienten gravedad en este contexto

class Proton(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='proton')

class Neutron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='neutron')

class Photon(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.05, particle_type='photon')

    def update(self, dt):
        self.position += self.velocity * dt  # Viaja a la velocidad de la luz (en este caso representativa)
        # No hay gravedad ni rebote para los fotones

class FluidSphere(Sphere):
    def __init__(self, position, velocity, radius):
        super().__init__(position, velocity, radius, particle_type='fluid')

    def deform(self):
        # Método para simular la deformación de la esfera cuando actúa como un fluido
        self.radius *= 1.1  # Aumentar el tamaño de la esfera para simular fluido

    def simulate_fluid_behavior(self, other):
        distance = np.linalg.norm(self.position - other.position)
        if distance < self.radius + other.radius:
            # Lógica para fusionar o interactuar como fluidos
            self.radius = (self.radius + other.radius) / 2  # Promedio de radios
            self.velocity = (self.velocity + other.velocity) / 2  # Promedio de velocidades


