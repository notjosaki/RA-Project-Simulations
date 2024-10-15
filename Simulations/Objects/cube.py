import numpy as np

class Cube:
    def __init__(self, position, velocity, size):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.size = size  # Tamaño del cubo (longitud de la arista)
        self.half_size = size / 2  # Para facilitar las colisiones y el manejo de límites

    def update(self, dt):
        self.position += self.velocity * dt
        self.velocity[1] -= 9.81 * dt  # Efecto de la gravedad

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.half_size < 0:
            self.position[1] = self.half_size
            self.velocity[1] = -self.velocity[1] * 0.9  # Pérdida de energía al rebotar

    def check_collision(self, other):
        # Chequeo de colisión basado en los límites de los cubos
        overlap_x = abs(self.position[0] - other.position[0]) < (self.half_size + other.half_size)
        overlap_y = abs(self.position[1] - other.position[1]) < (self.half_size + other.half_size)
        overlap_z = abs(self.position[2] - other.position[2]) < (self.half_size + other.half_size)

        return overlap_x and overlap_y and overlap_z

    def resolve_collision(self, other):
        # Resolver colisión intercambiando velocidades en la dirección del eje más cercano
        normal = self.position - other.position
        normal = normal / np.linalg.norm(normal)  # Normalizar la dirección

        relative_velocity = self.velocity - other.velocity
        velocity_along_normal = np.dot(relative_velocity, normal)

        if velocity_along_normal > 0:
            return  # No hay colisión si están alejándose

        restitution = 0.9  # Coeficiente de restitución
        j = -(1 + restitution) * velocity_along_normal
        j /= (1 / self.size + 1 / other.size)

        impulse = j * normal
        self.velocity -= impulse / self.size
        other.velocity += impulse / other.size
