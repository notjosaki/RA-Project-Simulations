import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Astro:
    def __init__(self, massa, position=(0, 0), radius=0.5, color=(0.2, 0.6, 1.0)):
        self.massa = massa
        self.position = np.array(position, dtype=float)  # Posición en el plano
        self.radius = radius
        self.color = color

    def draw(self):
        """Dibujar el astro como una esfera."""
        glColor3f(*self.color)  # Color del astro
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
                deformation = schwarzschild_radius / (distance + 1e-6)
                z -= deformation * 1000  # Escalar para visualizar
            deformed_grid[i] = [x, y, z]
    return deformed_grid


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


def setup_camera(zoom):
    """Configurar la cámara para una vista 3D inclinada."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Configuración de la cámara con una vista inclinada y zoom
    gluLookAt(
        0, -30 + zoom, 30 + zoom,  # Posición de la cámara (x, y, z)
        0, 0, 0,                   # Hacia dónde mira la cámara (centro de la escena)
        0, 0, 1                    # Vector "arriba" (orientación)
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Curvatura del Espacio-Tiempo (Vista 3D)')

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Crear astros
    astro1 = Astro(massa=5.97e24, position=(-3, 0), radius=1.0, color=(0.2, 0.6, 1.0))  # Astro 1
    astro2 = Astro(massa=5.97e24, position=(3, 0), radius=1.0, color=(1.0, 0.6, 0.2))  # Astro 2

    astros = [astro1, astro2]

    # Crear malla inicial
    grid = generate_grid(size=20, spacing=0.8)

    clock = pygame.time.Clock()
    move_speed = 5.0
    zoom = 0  # Zoom inicial

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda hacia arriba
                    zoom -= 1.0  # Acercar (zoom in)
                elif event.button == 5:  # Rueda hacia abajo
                    zoom += 1.0  # Alejar (zoom out)

        # Movimiento del astro 1 con teclas de flecha
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            astro1.position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_DOWN]:
            astro1.position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_LEFT]:
            astro1.position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_RIGHT]:
            astro1.position[0] += move_speed * clock.get_time() / 1000.0

        # Movimiento del astro 2 con teclas WASD
        if keys[K_w]:
            astro2.position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_s]:
            astro2.position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_a]:
            astro2.position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_d]:
            astro2.position[0] += move_speed * clock.get_time() / 1000.0

        # Deformar la malla según las posiciones de los astros
        deformed_grid = deform_grid(grid, astros)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Configurar cámara con zoom
        setup_camera(zoom)

        # Dibujar la malla deformada
        draw_grid(deformed_grid)

        # Dibujar los astros
        for astro in astros:
            astro.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
