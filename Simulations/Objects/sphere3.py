import numpy as np
import glm

class Sphere:
    def __init__(self, position, velocity, radius, particle_type='default', mass=1.0, charge=0.0):
        self.position = np.array(position, dtype=np.float64)
        self.previous_position = np.copy(self.position)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.particle_type = particle_type
        self.mass = mass
        self.charge = charge  # Carga de la partícula
        self.energy = 0  # Energía de la partícula

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

class Electron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.1, particle_type='electron', mass=9.11e-31, charge=-1.6e-19)

    def handle_particle_interaction(self, other):
        if other.particle_type == 'proton':
            self.velocity += 0.1 * (other.position - self.position) / np.linalg.norm(other.position - self.position)
        elif other.particle_type == 'photon':
            energy_transfer = other.calculate_energy() * 0.1
            self.energy += energy_transfer
            other.velocity *= 0.9

    def apply_electromagnetic_force(self, other):
        k = 8.9875517873681764e9  # Constante de Coulomb
        distance_vector = glm.dvec3(*other.position) - glm.dvec3(*self.position)
        distance = glm.length(distance_vector)
        if distance > 0:
            force_magnitude = k * (self.charge * other.charge) / (distance ** 2)
            force_direction = glm.normalize(distance_vector)
            return force_direction * force_magnitude  # Atrae o repele dependiendo de las cargas
        return glm.dvec3(0.0)

class Proton(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='proton', mass=1.67e-27, charge=1.6e-19)

    def handle_particle_interaction(self, other):
        if other.particle_type == 'electron':
            energy_transfer = self.calculate_energy() * 0.05
            self.energy -= energy_transfer
            other.energy += energy_transfer

class Neutron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='neutron', mass=1.67e-27, charge=0)

    def handle_particle_interaction(self, other):
        if other.particle_type in ['proton', 'electron']:
            energy_transfer = self.calculate_energy() * 0.03
            self.energy -= energy_transfer
            other.energy += energy_transfer

class Photon(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.05, particle_type='photon', mass=0, charge=0)

    def apply_force(self, force, dt):
        pass

    def update(self, dt):
        self.position += self.velocity * dt

    def handle_particle_interaction(self, other):
        if isinstance(other, Sphere) and other.mass > 0:
            energy_transfer = self.calculate_energy() * 0.1
            other.energy += energy_transfer
            self.velocity = np.zeros(3)

class HiggsBoson(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.3, particle_type='Higgs Boson', mass=2.2e-25, charge=0)

    def handle_particle_interaction(self, other):
        if other.particle_type in ['electron', 'proton']:
            energy_transfer = self.calculate_energy() * 0.05
            self.energy -= energy_transfer
            other.energy += energy_transfer
