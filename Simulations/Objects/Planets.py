import numpy as np
import glm

class Sphere:
    def __init__(self, position, velocity, radius, particle_type='default', mass=1.0, charge=0.0, energy=0):
        self.position = np.array(position, dtype=np.float64)
        self.previous_position = np.copy(self.position)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.particle_type = particle_type
        self.mass = mass
        self.charge = charge  
        self.energy = energy  

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def update(self, dt, gravity=9.81):
        self.previous_position = np.copy(self.position)
        self.position += self.velocity * dt
        self.velocity[1] -= gravity * dt

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Rebote

    def check_swept_collision(self, other):
        displacement_self = glm.dvec3(*self.position) - glm.dvec3(*self.previous_position)
        displacement_other = glm.dvec3(*other.position) - glm.dvec3(*other.previous_position)
        relative_displacement = displacement_self - displacement_other
        initial_vector = glm.dvec3(*self.previous_position) - glm.dvec3(*other.previous_position)
        distance_at_closest_approach = glm.dot(initial_vector, glm.normalize(relative_displacement))
        return distance_at_closest_approach < self.radius + other.radius

    def resolve_collision(self, other):
        collision_vector = glm.dvec3(*self.position) - glm.dvec3(*other.position)
        distance = glm.length(collision_vector)
        min_distance = self.radius + other.radius
        if distance < min_distance:
            collision_normal = glm.normalize(collision_vector)
            overlap = min_distance - distance
            self.position += collision_normal * overlap * 0.5
            other.position -= collision_normal * overlap * 0.5
            relative_velocity = self.velocity - other.velocity
            velocity_along_normal = glm.dot(glm.dvec3(*relative_velocity), collision_normal)
            if velocity_along_normal > 0:
                return
            restitution = 0.8
            impulse_magnitude = -(1 + restitution) * velocity_along_normal
            impulse_magnitude /= (1 / self.mass + 1 / other.mass)
            impulse = collision_normal * impulse_magnitude
            self.velocity += impulse / self.mass
            other.velocity -= impulse / other.mass

    def handle_particle_interaction(self, other):
        pass

    def calculate_energy(self):
        return 0.5 * self.mass * np.linalg.norm(self.velocity) ** 2

    def apply_gravitational_force(self, other):
        G = 6.67430e-11  # Constante de gravitación
        distance_vector = glm.dvec3(*other.position) - glm.dvec3(*self.position)
        distance = glm.length(distance_vector)
        if distance > 0:
            force_magnitude = G * (self.mass * other.mass) / (distance ** 2)
            force_direction = glm.normalize(distance_vector)
            return force_direction * force_magnitude
        return glm.dvec3(0.0)

class Planet(Sphere):
    def __init__(self, position, velocity, radius, mass, name='Planet', charge=0.0, atmosphere=None):
        super().__init__(position, velocity, radius, particle_type='planet', mass=mass, charge=charge)
        self.name = name  # Nombre del planeta
        self.atmosphere = atmosphere  # Información sobre la atmósfera

    def apply_gravitational_force(self, other):
        # Aplica la fuerza gravitacional de este planeta a otro objeto
        force = super().apply_gravitational_force(other)
        other.apply_force(force, dt=1.0)  # Aplica la fuerza al otro objeto, puedes modificar el dt

    def update(self, dt, gravity=9.81):
        # Aquí puedes modificar cómo los planetas actualizan su posición y velocidad si es necesario
        super().update(dt, gravity)

    def draw(self):
        # Método para representar el planeta gráficamente (implementación personalizada)
        # Ejemplo: dibujar una esfera con un color específico según el tipo de planeta
        # Aquí deberías usar tu sistema de gráficos, como Pygame o OpenGL.
        pass

    def get_info(self):
        return {
            'name': self.name,
            'position': self.position,
            'velocity': self.velocity,
            'mass': self.mass,
            'radius': self.radius,
            'charge': self.charge,
            'atmosphere': self.atmosphere
        }

# Ejemplo de creación de un planeta
earth = Planet(position=[0, 10, 0], velocity=[0, 0, 0], radius=1, mass=5.972e24, name='Earth', atmosphere='Nitrogen-Oxygen')
