import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Astro:
    def __init__(self, massa, position=(0, 0), radius=0.5, color=(0.2, 0.6, 1.0), texture=None):
        self.massa = massa
        self.position = np.array(position, dtype=float)  # Posición en el plano
        self.radius = radius
        self.color = color
        self.texture = texture

    def draw(self):
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.radius)

        if self.texture:  # Si hay textura, aplicarla
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            gluQuadricTexture(quadric, GL_TRUE)
            glColor3f(1.0, 1.0, 1.0)  # Color blanco para evitar mezcla de colores
        else:  # Si no hay textura, usar color sólido
            glColor3f(*self.color)

        gluSphere(quadric, self.radius, 32, 32)

        if self.texture:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()



def load_texture(image_path):
    """Cargar una textura desde un archivo."""
    texture_surface = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width, height = texture_surface.get_size()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture


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
            
            if distance > astro.radius:  # Solo deformar puntos fuera del radio del planeta
                schwarzschild_radius = 2 * G * astro.massa / c**2
                deformation = schwarzschild_radius / (distance + 1e-6)  # Gravedad decrece con la distancia
                
                # Aseguramos que la deformación siempre resta al eje Z
                z_new = z - deformation * 5000  # Escalar para visualización
                z = min(z, z_new)  # El nuevo Z nunca puede ser mayor que el actual

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

    # Cargar textura de Marte
    texture_earth = load_texture("earth.png")
    textura_marte = load_texture("textura_marte.png")

    # Crear astros
    astro1 = Astro(massa=5.97e24, position=(-3, 0), radius=3.0, color=(0.2, 0.6, 1.0), texture=texture_earth)  # Astro 1 sin textura
    astro2 = Astro(massa=5.97e24, position=(3, 0), radius=3.5, color=(1.0, 0.6, 0.2), texture=textura_marte)  # Astro 2 con textura

    astros = [astro1, astro2]

    # Crear malla inicial
    grid = generate_grid(size=20, spacing=0.8)

    clock = pygame.time.Clock()
    zoom = 0
    min_zoom = -30
    max_zoom = 25

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda hacia arriba (zoom in)
                    zoom -= 1.0
                elif event.button == 5:  # Rueda hacia abajo (zoom out)
                    zoom += 1.0

        zoom = max(min_zoom, min(max_zoom, zoom))

        # Capturar las teclas presionadas
        keys = pygame.key.get_pressed()

        # Movimiento del astro 1 con teclas de flecha
        move_speed = 5.0  # Velocidad de movimiento
        if keys[K_UP]:
            astros[0].position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_DOWN]:
            astros[0].position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_LEFT]:
            astros[0].position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_RIGHT]:
            astros[0].position[0] += move_speed * clock.get_time() / 1000.0

        # Movimiento del astro 2 con teclas WASD
        if keys[K_w]:
            astros[1].position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_s]:
            astros[1].position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_a]:
            astros[1].position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_d]:
            astros[1].position[0] += move_speed * clock.get_time() / 1000.0

        # Deformar la malla según las posiciones de los astros
        deformed_grid = deform_grid(grid, astros)

        # Dibujar la escena
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_camera(zoom)
        draw_grid(deformed_grid)
        for astro in astros:
            astro.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

