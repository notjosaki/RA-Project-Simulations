import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Astro:
    def __init__(self, massa, position=(0, 0), radius=0.5, color=(0.2, 0.6, 1.0)):
        self.massa = massa
        self.position = np.array([*position, 0], dtype=float)  # Añadimos Z
        self.radius = radius
        self.color = color

    def draw(self):
        """Dibujar el astro como una esfera."""
        glColor3f(*self.color)
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()


def generate_grid(size=20, spacing=0.5):
    """Generar una malla de puntos para representar el espacio-tiempo."""
    grid = []
    for x in np.linspace(-size, size, int(2 * size / spacing)):
        for y in np.linspace(-size, size, int(2 * size / spacing)):
            grid.append([x, y, 0])
    return np.array(grid)


def deform_grid(grid, astros, G=6.674e-11, c=3e8):
    """Deformar la malla según la curvatura gravitacional de múltiples astros."""
    deformed_grid = grid.copy()
    for astro in astros:
        for i, point in enumerate(deformed_grid):
            x, y, z = point
            dx, dy = astro.position[0] - x, astro.position[1] - y
            distance = np.sqrt(dx**2 + dy**2)
            if distance > astro.radius:
                schwarzschild_radius = 2 * G * astro.massa / c**2
                deformation = -schwarzschild_radius / (distance + 1e-6)
                z += deformation * 1000  # Escalar para visualizar
            deformed_grid[i] = [x, y, z]
    return deformed_grid


def update_astro_position(astro, grid, G=6.674e-11, c=3e8):
    """Actualizar la posición Z del astro según la malla deformada."""
    x, y = astro.position[0], astro.position[1]
    dx = grid[:, 0] - x
    dy = grid[:, 1] - y
    distances = np.sqrt(dx**2 + dy**2)
    nearest_index = np.argmin(distances)
    nearest_point = grid[nearest_index]

    schwarzschild_radius = 2 * G * astro.massa / c**2
    deformation = -schwarzschild_radius / (distances[nearest_index] + 1e-6)
    astro.position[2] = nearest_point[2] + deformation * 1000  # Ajuste en Z


def draw_grid(grid, color=(1, 1, 1)):
    """Dibujar la malla como una red de líneas."""
    glColor3f(*color)
    glBegin(GL_LINES)
    size = int(np.sqrt(len(grid)))
    for i in range(size):
        for j in range(size - 1):
            glVertex3f(*grid[i * size + j])
            glVertex3f(*grid[i * size + (j + 1)])
            glVertex3f(*grid[j * size + i])
            glVertex3f(*grid[(j + 1) * size + i])
    glEnd()


def setup_camera(zoom):
    """Configurar la cámara para una vista 3D inclinada."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -30 + zoom, 30 + zoom, 0, 0, 0, 0, 0, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Curvatura del Espacio-Tiempo (Vista 3D)')

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    astro1 = Astro(massa=5.97e24, position=(-3, 0), radius=1.0, color=(0.2, 0.6, 1.0))
    astro2 = Astro(massa=5.97e24, position=(3, 0), radius=1.0, color=(1.0, 0.6, 0.2))
    astros = [astro1, astro2]

    grid = generate_grid(size=20, spacing=0.8)

    clock = pygame.time.Clock()
    zoom = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom -= 1.0
                elif event.button == 5:
                    zoom += 1.0

        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            astro1.position[1] += 5 * clock.get_time() / 1000.0
        if keys[K_DOWN]:
            astro1.position[1] -= 5 * clock.get_time() / 1000.0
        if keys[K_LEFT]:
            astro1.position[0] -= 5 * clock.get_time() / 1000.0
        if keys[K_RIGHT]:
            astro1.position[0] += 5 * clock.get_time() / 1000.0
        if keys[K_w]:
            astro2.position[1] += 5 * clock.get_time() / 1000.0
        if keys[K_s]:
            astro2.position[1] -= 5 * clock.get_time() / 1000.0
        if keys[K_a]:
            astro2.position[0] -= 5 * clock.get_time() / 1000.0
        if keys[K_d]:
            astro2.position[0] += 5 * clock.get_time() / 1000.0

        deformed_grid = deform_grid(grid, astros)

        for astro in astros:
            update_astro_position(astro, deformed_grid)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_camera(zoom)
        draw_grid(deformed_grid)
        for astro in astros:
            astro.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
