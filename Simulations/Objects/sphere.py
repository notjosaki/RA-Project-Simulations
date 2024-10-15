import numpy as np
class Sphere:
    def __init__(self, position, velocity, radius):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.radius = radius

    def update(self, dt):
        self.position += self.velocity * dt
        self.velocity[1] -= 9.81 * dt  # Efecto de la gravedad

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Pérdida de energía al rebotar

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
