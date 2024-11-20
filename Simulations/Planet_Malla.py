import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Astro:
    def __init__(self, massa, position=(0, 0), radius=0.5):
        self.massa = massa
        self.position = np.array(position, dtype=float)  # Posición en el plano
        self.radius = radius

    def draw(self):
        """Dibujar el astro como una esfera."""
        glColor3f(0.2, 0.6, 1.0)  # Color azul
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.radius)
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()


def generate_grid(size=20, spacing=0.5):
    """Generar una malla de puntos para representar el espacio-tiempo."""
    grid = []
    for x in np.linspace(-size, size, int(2 * size / spacing)):
        for y in np.linspace(-size, size, int(2 * size / spacing)):
            grid.append([x, y, 0])
    return np.array(grid)


def deform_grid(grid, astro, G=6.674e-11, c=3e8):
    """Deformar la malla según la curvatura gravitacional."""
    deformed_grid = []
    for point in grid:
        x, y, z = point
        dx, dy = astro.position[0] - x, astro.position[1] - y
        distance = np.sqrt(dx**2 + dy**2)
        if distance > astro.radius:
            # Calcular la curvatura usando el radio de Schwarzschild
            schwarzschild_radius = 2 * G * astro.massa / c**2
            deformation = schwarzschild_radius / (distance + 1e-6)
            z = -deformation * 1000  # Escalar para visualizar
        deformed_grid.append([x, y, z])
    return np.array(deformed_grid)


def draw_grid(grid, color=(1, 1, 1)):
    """Dibujar la malla como una red de líneas."""
    glColor3f(*color)
    glBegin(GL_LINES)
    size = int(np.sqrt(len(grid)))
    for i in range(size):
        for j in range(size - 1):
            # Líneas en dirección X
            glVertex3f(*grid[i * size + j])
            glVertex3f(*grid[i * size + (j + 1)])
            # Líneas en dirección Y
            glVertex3f(*grid[j * size + i])
            glVertex3f(*grid[(j + 1) * size + i])
    glEnd()


def setup_camera():
    """Configurar la cámara para una vista 3D inclinada."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Configuración de la cámara con una vista inclinada
    gluLookAt(
        0, -30, 30,  # Posición de la cámara (x, y, z)
        0, 0, 0,     # Hacia dónde mira la cámara (centro de la escena)
        0, 0, 1      # Vector "arriba" (orientación)
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Curvatura del Espacio-Tiempo (Vista 3D)')

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Crear astro
    astro = Astro(massa=5.97e24, position=(0, 0), radius=1.0)  # Tierra

    # Crear malla inicial
    grid = generate_grid(size=10, spacing=0.5)

    clock = pygame.time.Clock()
    move_speed = 5.0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        # Movimiento del astro
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            astro.position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_DOWN]:
            astro.position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_LEFT]:
            astro.position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_RIGHT]:
            astro.position[0] += move_speed * clock.get_time() / 1000.0

        # Deformar la malla según la posición del astro
        deformed_grid = deform_grid(grid, astro)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Configurar cámara
        setup_camera()

        # Dibujar la malla deformada
        draw_grid(deformed_grid)

        # Dibujar el astro
        astro.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()