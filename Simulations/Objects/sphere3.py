import numpy as np
from abc import ABC, abstractmethod
import glm  # Usaremos glm para manejar vectores y geometría de colisión

class Sphere(ABC):
    def __init__(self, position, velocity, radius, particle_type, mass):
        self.position = np.array(position, dtype=np.float32)
        self.previous_position = np.copy(self.position)  # Guardar posición anterior para colisiones barridas
        self.velocity = np.array(velocity, dtype=np.float32)
        self.radius = radius
        self.particle_type = particle_type
        self.mass = mass
        self.energy = 0  # Energía de la partícula

    @abstractmethod
    def apply_force(self, force, dt):
        pass

    def update(self, dt, gravity=9.81):
        self.previous_position = np.copy(self.position)  # Actualizamos la posición anterior
        self.position += self.velocity * dt
        self.velocity[1] -= gravity * dt

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Pérdida de energía al rebotar

    def check_collision(self, other):
        # Colisión estándar por distancia
        distance = np.linalg.norm(self.position - other.position)
        return distance < self.radius + other.radius

    def check_swept_collision(self, other):
        # Desplazamiento relativo entre los dos objetos
        relative_velocity = self.velocity - other.velocity
        relative_position = self.position - other.position
        
        # Coeficientes de la ecuación cuadrática
        a = np.dot(relative_velocity, relative_velocity)
        b = 2 * np.dot(relative_position, relative_velocity)
        c = np.dot(relative_position, relative_position) - (self.radius + other.radius) ** 2
        
        # Resolver la ecuación cuadrática: ax^2 + bx + c = 0
        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            return False  # No hay colisión, ya que el discriminante es negativo

        # Si hay solución, calcular los tiempos de colisión
        sqrt_discriminant = np.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)

        # Si ambos tiempos son negativos, las partículas no colisionarán en el futuro
        if t1 < 0 and t2 < 0:
            return False

        # Detectamos colisión antes de que los objetos se solapen (t1 o t2 deben ser positivos)
        return True


    def resolve_collision(self, other):
        # Vector entre los centros de las esferas
        collision_vector = glm.vec3(*self.position) - glm.vec3(*other.position)
        
        # Distancia entre centros
        distance = glm.length(collision_vector)
        
        # Distancia mínima para colisión
        min_distance = self.radius + other.radius
        
        # Si hay colisión
        if distance < min_distance:
            # Normalizar el vector de colisión
            collision_normal = glm.normalize(collision_vector)
            
            # Separar las esferas para que dejen de colisionar
            overlap = min_distance - distance
            self.position += collision_normal * overlap * 0.5
            other.position -= collision_normal * overlap * 0.5
            
            # Intercambiar velocidades en la dirección de la colisión
            relative_velocity = self.velocity - other.velocity
            velocity_along_normal = glm.dot(glm.vec3(*relative_velocity), collision_normal)
            
            # Si las esferas se están alejando, no hacemos nada
            if velocity_along_normal > 0:
                return
            
            # Impulso de la colisión (con conservación del momento)
            restitution = 0.8  # Coeficiente de restitución
            impulse_magnitude = -(1 + restitution) * velocity_along_normal
            impulse_magnitude /= (1 / self.mass + 1 / other.mass)
            
            # Aplicar impulso
            impulse = collision_normal * impulse_magnitude
            self.velocity += impulse / self.mass
            other.velocity -= impulse / other.mass

    @abstractmethod
    def handle_particle_interaction(self, other):
        pass

    def calculate_energy(self):
        # Calcular energía cinética
        return 0.5 * self.mass * np.linalg.norm(self.velocity) ** 2


class Electron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.1, particle_type='electron', mass=9.11e-31)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        if other.particle_type == 'proton':
            self.velocity += 0.1 * (other.position - self.position) / np.linalg.norm(other.position - self.position)
        elif other.particle_type == 'photon':
            energy_transfer = other.calculate_energy() * 0.1
            self.energy += energy_transfer
            other.velocity *= 0.9


class Proton(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='proton', mass=1.67e-27)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        if other.particle_type == 'electron':
            energy_transfer = self.calculate_energy() * 0.05
            self.energy -= energy_transfer
            other.energy += energy_transfer


class Neutron(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.2, particle_type='neutron', mass=1.67e-27)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        if other.particle_type in ['proton', 'electron']:
            energy_transfer = self.calculate_energy() * 0.03
            self.energy -= energy_transfer
            other.energy += energy_transfer


class Photon(Sphere):
    def __init__(self, position, velocity):
        super().__init__(position, velocity, radius=0.05, particle_type='photon', mass=0)

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
        super().__init__(position, velocity, radius=0.3, particle_type='Higgs Boson', mass=2.2e-25)

    def apply_force(self, force, dt):
        acceleration = force / self.mass
        self.velocity += acceleration * dt

    def handle_particle_interaction(self, other):
        if other.particle_type in ['electron', 'proton']:
            energy_transfer = self.calculate_energy() * 0.05
            self.energy -= energy_transfer
            other.energy += energy_transfer
