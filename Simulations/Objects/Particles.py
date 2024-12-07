import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class Particle:
    def __init__(self, position, texture_id, velocity=None, radius=0.05):
        """
        Inicializa una partícula con su posición, textura, velocidad y radio.
        
        Args:
            position (tuple): La posición inicial (x, y, z).
            texture_id (int): El ID de la textura OpenGL.
            velocity (tuple, opcional): Velocidad inicial (vx, vy, vz). Generada aleatoriamente si no se proporciona.
            radius (float, opcional): Radio de la partícula.
        """
        self.position = np.array(position, dtype=float)
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius
        self.texture_id = texture_id

    def update(self, speed_factor=1.0):
        """
        Actualiza la posición de la partícula aplicando la velocidad.
        
        Args:
            speed_factor (float, opcional): Factor de velocidad global.
        """
        self.position += self.velocity * speed_factor

        # Verificar colisiones con las paredes (limites -1 a 1 en cada eje)
        for i in range(3):  # Para x, y, z
            if self.position[i] + self.radius > 1 or self.position[i] - self.radius < -1:
                self.velocity[i] = -self.velocity[i]

    def check_collision(self, other_particle):
        """
        Verifica si esta partícula ha colisionado con otra.
        
        Args:
            other_particle (Particle): Otra partícula.
        
        Returns:
            bool: True si hay colisión, False de lo contrario.
        """
        distance = np.linalg.norm(self.position - other_particle.position)
        return distance < (self.radius + other_particle.radius)

    def interact(self, other_particle, spheres, textures):
        """
        Define las interacciones personalizadas entre dos partículas.
        
        Args:
            other_particle (Particle): Otra partícula.
            spheres (list): Lista de todas las partículas existentes.
            textures (dict): Diccionario de texturas.
        """
        if self.texture_id == textures['lepton'] and other_particle.texture_id == textures['boson']:
            # Lepton + Boson → Desintegración y creación de nuevas partículas
            spheres.remove(self)
            spheres.remove(other_particle)
            for _ in range(3):  # Crear 3 partículas secundarias
                secondary_velocity = np.random.uniform(-0.01, 0.01, 3)
                spheres.append(Particle(self.position, textures['neutron'], velocity=secondary_velocity, radius=0.02))
        
        elif (self.texture_id == textures['proton'] and other_particle.texture_id == textures['quark']) or \
             (self.texture_id == textures['quark'] and other_particle.texture_id == textures['proton']):
            # Proton + Quark → Fusión en Higgs
            self.texture_id = textures['higgs']
            spheres.remove(other_particle)
        
        elif self.texture_id == textures['neutron'] or other_particle.texture_id == textures['neutron']:
            # Neutron → Repulsión
            self.velocity = -self.velocity
            other_particle.velocity = -other_particle.velocity

    def draw(self):
        """
        Dibuja la partícula como una esfera con textura.
        """
        slices = 20
        stacks = 20
        glPushMatrix()
        glTranslatef(*self.position)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, self.radius, slices, stacks)

        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
