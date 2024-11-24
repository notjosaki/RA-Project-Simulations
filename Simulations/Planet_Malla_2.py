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
            
            # Eliminar vértices dentro del radio del astro
            if distance < astro.radius:
                deformed_grid[i] = [x, y, None]  # Marca como None para no dibujar
                continue
            
            # Suavizar deformación
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
            if grid[i * size + j][2] is not None and grid[i * size + (j + 1)][2] is not None:
                glVertex3f(*grid[i * size + j])
                glVertex3f(*grid[i * size + (j + 1)])


            # Líneas en dirección Y
            if grid[j * size + i][2] is not None and grid[(j + 1) * size + i][2] is not None:
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


def draw_slider(x, y, width, height, value, min_val, max_val):
    """Dibujar una barra deslizante en la pantalla para controlar el tamaño del planeta."""
    pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height))  # Fondo de la barra
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))  # Contorno de la barra
    # Dibuja el deslizador
    slider_pos = x + (value - min_val) / (max_val - min_val) * width
    pygame.draw.circle(screen, (255, 0, 0), (int(slider_pos), y + height // 2), 10)


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Curvatura del Espacio-Tiempo (Vista 3D)')

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Crear astros
    astro1 = Astro(massa=5.97e24, position=(0, 0), radius=2.0, color=(0.2, 0.6, 1.0))  # Astro 1
    astros = [astro1]

    # Crear malla inicial
    grid = generate_grid(size=20, spacing=0.5)

    clock = pygame.time.Clock()
    zoom = 0  # Zoom inicial

    # Configuración de la barra deslizante
    slider_x = 50
    slider_y = 500
    slider_width = 500
    slider_height = 20
    slider_value = astro1.radius  # Valor inicial basado en el radio del astro
    slider_min = 0.5  # Radio mínimo
    slider_max = 5.0  # Radio máximo

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Si se hace clic en la barra deslizante
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
                        # Actualizar el valor del slider
                        slider_value = (mouse_x - slider_x) / slider_width * (slider_max - slider_min) + slider_min
                        astro1.radius = slider_value  # Actualizar el radio del astro

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

        # Dibujar la barra deslizante para cambiar el tamaño del planeta
        draw_slider(slider_x, slider_y, slider_width, slider_height, slider_value, slider_min, slider_max)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
