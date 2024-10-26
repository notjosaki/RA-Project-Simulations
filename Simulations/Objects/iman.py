import numpy as np
import glm

class Iman:
    def __init__(self, position, strength, polarity):
        self.position = np.array(position, dtype=np.float64)  # Posición del imán
        self.strength = strength  # Fuerza del imán
        self.polarity = polarity  # 'N' para norte, 'S' para sur

    def atraer(self, particle):
        """Aplica una fuerza electromagnética a una partícula."""
        if isinstance(particle, Sphere):
            # Calcula la dirección hacia el imán
            distance_vector = glm.dvec3(*self.position) - glm.dvec3(*particle.position)
            distance = glm.length(distance_vector)

            if distance > 0:
                # Normaliza el vector de distancia para obtener la dirección
                force_direction = glm.normalize(distance_vector)

                # Calcula la fuerza en función de la polaridad del imán y la carga de la partícula
                force_magnitude = self.strength * (1 if self.polarity == 'N' and particle.charge < 0 else -1)
                force = force_direction * force_magnitude

                # Aplica la fuerza a la partícula
                particle.apply_force(force, dt=0.01)  # Puedes ajustar el dt según sea necesario

    def __str__(self):
        return f"Imán: Posición: {self.position}, Fuerza: {self.strength}, Polaridad: {self.polarity}"


