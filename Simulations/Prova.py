import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *  # Importa GLU para usar gluLookAt
import pygame
from pygame.locals import *
import time

# Definición de la clase Box para los rebotes con pérdida de energía
class Box:
    def __init__(self, center, size, energy_loss=0.9):
        self.center = np.array(center, dtype=np.float64)
        self.size = size  # tamaño del cubo
        self.energy_loss = energy_loss  # pérdida de energía en cada rebote

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.center)
        self.draw_box()
        glPopMatrix()

    def draw_box(self):
        """Dibuja un cubo alámbrico."""
        half_size = self.size
        vertices = [
            (-half_size, -half_size, -half_size),
            ( half_size, -half_size, -half_size),
            ( half_size,  half_size, -half_size),
            (-half_size,  half_size, -half_size),
            (-half_size, -half_size,  half_size),
            ( half_size, -half_size,  half_size),
            ( half_size,  half_size,  half_size),
            (-half_size,  half_size,  half_size),
        ]
        
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # cara inferior
            (4, 5), (5, 6), (6, 7), (7, 4),  # cara superior
            (0, 4), (1, 5), (2, 6), (3, 7)   # conexiones verticales
        ]

        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

    def collide(self, sphere):
        """Detecta colisiones con las paredes de la caja y ajusta la velocidad de la esfera."""
        for i in range(3):  # Comprueba cada eje (x, y, z)
            if abs(sphere.position[i] - self.center[i]) + sphere.radius >= self.size:
                sphere.velocity[i] = -sphere.velocity[i] * self.energy_loss  # Rebote con pérdida de energía

# Clase Sphere
class Sphere:
    def __init__(self, position, velocity, radius, mass=1.0):
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.mass = mass

    def update(self, dt):
        """Actualiza la posición de la esfera."""
        self.position += self.velocity * dt

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        self.draw_sphere()
        glPopMatrix()

    def draw_sphere(self):
        """Dibuja una esfera usando glBegin y glEnd."""
        slices = 16
        stacks = 16
        for i in range(slices):
            lat0 = np.pi * (-0.5 + float(i) / slices)  # latitud
            z0 = np.sin(lat0)  # z
            zr0 = np.cos(lat0)  # radio en z

            lat1 = np.pi * (-0.5 + float(i + 1) / slices)  # latitud
            z1 = np.sin(lat1)  # z
            zr1 = np.cos(lat1)  # radio en z

            glBegin(GL_QUAD_STRIP)
            for j in range(stacks + 1):
                lng = 2 * np.pi * float(j) / stacks  # longitud
                x = np.cos(lng)  # x
                y = np.sin(lng)  # y

                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0 * self.radius, y * zr0 * self.radius, z0 * self.radius)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1 * self.radius, y * zr1 * self.radius, z1 * self.radius)
            glEnd()

# Función principal para simular el rebote
def main():
    # Inicialización de Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Rebote en caja')

    glEnable(GL_DEPTH_TEST)

    # Crear objetos
    box = Box(center=(0, 0, 0), size=10, energy_loss=0.8)
    sphere = Sphere(position=(1, 2, 3), velocity=(1, -1.5, 1.2), radius=0.5)

    gluLookAt(20, 20, 20, 0, 0, 0, 0, 1, 0)

    # Bucle principal
    last_time = time.time()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Actualiza la esfera y verifica colisiones
        current_time = time.time()
        dt = current_time - last_time
        sphere.update(dt)
        box.collide(sphere)  # Comprobar colisiones y aplicar rebote
        last_time = current_time

        # Dibujar la caja y la esfera
        box.draw()
        sphere.draw()

        # Actualizar la pantalla
        pygame.display.flip()
        pygame.time.wait(16)  # Espera para limitar el frame rate

    pygame.quit()

if __name__ == "__main__":
    main()
