import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np

# Definir los vértices y las aristas del cubo
vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Clase para representar esferas
class Sphere:
    def __init__(self, position, velocity=None, radius=0.05):
        self.position = np.array(position, dtype=float)
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius

    def update(self):
        """Actualiza la posición de la esfera y maneja colisiones."""
        # Actualizar la posición
        self.position += self.velocity

        # Comprobar colisiones con las paredes del cubo
        for i in range(3):  # Para x, y, z
            if self.position[i] + self.radius > 1 or self.position[i] - self.radius < -1:
                self.velocity[i] = -self.velocity[i]  # Invertir dirección

    def draw(self):
        """Dibuja la esfera en su posición."""
        slices = 10
        stacks = 10
        glPushMatrix()
        glTranslatef(*self.position)  # Mover la esfera a su posición
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, self.radius, slices, stacks)
        glPopMatrix()

    def check_collision(self, other):
        """Comprueba si hay colisión con otra esfera."""
        distance = np.linalg.norm(self.position - other.position)
        if distance < self.radius + other.radius:
            # Colisión detectada, invierte la dirección de las velocidades
            self.velocity, other.velocity = other.velocity, self.velocity

def draw_cube():
    """Dibuja un cubo utilizando las aristas definidas."""
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def setup_view(x_offset, y_offset, angle_x, angle_y):
    """Configura la vista en 3D."""
    glViewport(x_offset, y_offset, 400, 400)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)  # Perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)  # Posición de la cámara
    glRotatef(angle_x, 1, 0, 0)  # Rotar alrededor del eje X
    glRotatef(angle_y, 0, 1, 0)  # Rotar alrededor del eje Y

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Cubo 3D con Esferas en Movimiento')

    glClearColor(0.1, 0.1, 0.1, 1.0)  # Fondo oscuro
    glEnable(GL_DEPTH_TEST)  # Activar el test de profundidad

    spheres = []  # Lista para almacenar las esferas

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                # Generar una posición aleatoria dentro del cubo
                x = random.uniform(-0.9, 0.9)
                y = random.uniform(-0.9, 0.9)
                z = random.uniform(-0.9, 0.9)
                spheres.append(Sphere((x, y, z)))  # Añadir una nueva esfera

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Actualizar y dibujar las esferas
        for sphere in spheres:
            sphere.update()

        # Comprobar colisiones entre esferas
        for i in range(len(spheres)):
            for j in range(i + 1, len(spheres)):
                spheres[i].check_collision(spheres[j])

        # Dibujar las diferentes vistas
        # Vista frontal
        setup_view(0, 400, 0, 0)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        # Vista lateral
        setup_view(400, 400, 0, 90)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        # Vista superior
        setup_view(0, 0, 90, 0)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        # Vista isométrica
        setup_view(400, 0, 30, 45)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        pygame.display.flip()  # Actualizar la pantalla
        pygame.time.wait(10)  # Esperar un poco para la próxima actualización

if __name__ == "__main__":
    main()




