import numpy as np
import glm

import numpy as np
import glm

import numpy as np
import glm

class Cube:
    def __init__(self, position, velocity, size, mass=1.0):
        self.position = np.array(position)
        self.previous_position = np.array(position)  # Posición previa para detectar colisiones continuas
        self.velocity = np.array(velocity)
        self.size = size  # Tamaño del cubo (longitud de la arista)
        self.half_size = size / 2  # Para facilitar las colisiones y el manejo de límites
        self.mass = mass  # Masa del cubo

    def update(self, dt):
        self.previous_position = np.copy(self.position)  # Guardamos la posición anterior
        self.position += self.velocity * dt
        self.velocity[1] -= 9.81 * dt  # Efecto de la gravedad

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.half_size < 0:
            self.position[1] = self.half_size
            self.velocity[1] = -self.velocity[1] * 0.9  # Pérdida de energía al rebotar

    def check_swept_collision(self, other):
        # Vector de desplazamiento
        displacement_self = self.position - self.previous_position
        displacement_other = other.position - other.previous_position
        
        # Desplazamiento relativo entre los dos cubos
        relative_displacement = displacement_self - displacement_other

        # Vector entre las posiciones iniciales de ambos cubos
        initial_vector = glm.vec3(*self.previous_position) - glm.vec3(*other.previous_position)

        # Calculamos si las trayectorias de los cubos los llevan a una colisión
        distance_at_closest_approach = glm.dot(initial_vector, glm.normalize(relative_displacement))
        if distance_at_closest_approach < self.half_size + other.half_size:
            return True
        return False

    def resolve_collision(self, other):
        # Vector entre los centros de los dos cubos
        collision_vector = glm.vec3(*self.position) - glm.vec3(*other.position)
        
        # Distancia entre centros
        distance = glm.length(collision_vector)
        
        # Distancia mínima para colisión (considerando las mitades de los cubos)
        min_distance = self.half_size + other.half_size
        
        # Si están colisionando
        if distance < min_distance:
            # Normalizar el vector de colisión
            collision_normal = glm.normalize(collision_vector)
            
            # Empujar los cubos para que dejen de colisionar
            overlap = min_distance - distance
            self.position += collision_normal * overlap * 0.5
            other.position -= collision_normal * overlap * 0.5
            
            # Intercambiar velocidades en la dirección de la colisión (con conservación de momento)
            relative_velocity = self.velocity - other.velocity
            velocity_along_normal = glm.dot(glm.vec3(*relative_velocity), collision_normal)
            
            # Solo resolver si los objetos se están acercando (evitar resolución doble)
            if velocity_along_normal > 0:
                return
            
            # Calcular el impulso de la colisión
            restitution = 0.8  # Coeficiente de restitución (elasticidad del choque)
            impulse_magnitude = -(1 + restitution) * velocity_along_normal
            impulse_magnitude /= (1 / self.mass + 1 / other.mass)
            
            # Aplicar el impulso a ambos cubos
            impulse = collision_normal * impulse_magnitude
            self.velocity += impulse / self.mass
            other.velocity -= impulse / other.mass


