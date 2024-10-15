# sphere.py

import numpy as np

class Sphere:
    def __init__(self, position, velocity, radius):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.radius = radius

    def update(self, dt):
        self.position += self.velocity * dt
        self.velocity[1] -= 9.81 * dt  # Gravity effect

        # Bounce on the ground (y=0 plane)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Energy loss when bouncing

    def check_collision(self, other):
        distance = np.linalg.norm(self.position - other.position)
        return distance < self.radius + other.radius

def resolve_collision(sphere1, sphere2):
    normal = sphere2.position - sphere1.position
    normal = normal / np.linalg.norm(normal)  # Normalize the direction

    relative_velocity = sphere1.velocity - sphere2.velocity
    velocity_along_normal = np.dot(relative_velocity, normal)

    if velocity_along_normal > 0:
        return

    restitution = 0.9
    j = -(1 + restitution) * velocity_along_normal
    j /= (1 / sphere1.radius + 1 / sphere2.radius)

    impulse = j * normal
    sphere1.velocity -= impulse / sphere1.radius
    sphere2.velocity += impulse / sphere2.radius
