import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Astro:
    def __init__(self, massa, position=(0, 0), radius=1.0):
        self.massa = massa
        self.position = np.array(position, dtype=float)
        self.radius = radius

    def draw(self):
        """Dibujar el astro como una esfera."""
        glColor3f(0.2, 0.6, 1.0)  # Color azul
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.radius)
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()

    def calculate_gravitational_influence(self, point, G=6.674e-11, c=3e8):
        """Calcular la intensidad de la curvatura gravitacional."""
        dx, dy = self.position[0] - point[0], self.position[1] - point[1]
        distance = np.sqrt(dx**2 + dy**2)
        if distance > 0:
            schwarzschild_radius = 2 * G * self.massa / c**2
            return schwarzschild_radius / distance
        return 0


def generate_grid(size=20, spacing=0.5):
    """Generar una malla de puntos para representar el espacio-tiempo."""
    grid = []
    for x in np.linspace(-size, size, int(2 * size / spacing)):
        for y in np.linspace(-size, size, int(2 * size / spacing)):
            grid.append([x, y, 0])
    return np.array(grid)


def deform_grid(grid, astro):
    """Deformar la malla según la curvatura gravitacional."""
    deformed_grid = []
    for point in grid:
        x, y, z = point
        influence = astro.calculate_gravitational_influence(point)
        z = -influence * 1000  # Escalar para visualizar
        deformed_grid.append([x, y, z])
    return np.array(deformed_grid)


def draw_grid_with_colors(grid, astro, max_influence=0.0001):
    """Dibujar la malla con colores basados en la curvatura gravitacional."""
    glBegin(GL_LINES)
    size = int(np.sqrt(len(grid)))
    for i in range(size - 1):
        for j in range(size - 1):
            # Puntos adyacentes en dirección X
            p1, p2 = grid[i * size + j], grid[i * size + (j + 1)]
            avg_influence_x = (astro.calculate_gravitational_influence(p1) + astro.calculate_gravitational_influence(p2)) / 2
            color_x = min(1.0, avg_influence_x / max_influence)
            glColor3f(color_x, 0.2, 1.0 - color_x)  # Gradiente basado en gravedad
            glVertex3f(*p1)
            glVertex3f(*p2)

            # Puntos adyacentes en dirección Y
            p1, p2 = grid[j * size + i], grid[(j + 1) * size + i]
            avg_influence_y = (astro.calculate_gravitational_influence(p1) + astro.calculate_gravitational_influence(p2)) / 2
            color_y = min(1.0, avg_influence_y / max_influence)
            glColor3f(color_y, 0.2, 1.0 - color_y)  # Gradiente basado en gravedad
            glVertex3f(*p1)
            glVertex3f(*p2)
    glEnd()


def setup_camera():
    """Configurar la cámara para una vista 3D inclinada."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        0, -30, 30,  # Posición de la cámara (x, y, z)
        0, 0, 0,     # Hacia dónde mira la cámara
        0, 0, 1      # Vector "arriba"
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Curvatura del Espacio-Tiempo con Colores')

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Crear astro (similar al planeta Tierra)
    astro = Astro(massa=5.97e24, position=(0, 0), radius=1.0)

    # Generar malla
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

        # Configurar la cámara
        setup_camera()

        # Dibujar la malla con colores
        draw_grid_with_colors(deformed_grid, astro)

        # Dibujar el astro
        astro.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
