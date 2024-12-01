import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

# Constantes para el anillo
TORUS_RADIUS_MAJOR = 3.0  # Radio mayor (distancia al centro del toro)
TORUS_RADIUS_OUTER = 0.3  # Radio externo (radio del tubo)
TORUS_RADIUS_INNER = 0.2  # Radio interno (grosor del tubo)
NUM_SEGMENTS_MAJOR = 64   # Divisiones alrededor del círculo mayor
NUM_SEGMENTS_MINOR = 32   # Divisiones alrededor del círculo menor

# Factores para hacer el toroide más ovalado
OVAL_FACTOR_X = 2.0  # Escala en el eje X
OVAL_FACTOR_Y = 1.0  # Escala en el eje Y

class Particle:
    def __init__(self, angle_major, angle_minor, angular_velocity_major, angular_velocity_minor):
        self.angle_major = angle_major
        self.angle_minor = angle_minor
        self.angular_velocity_major = angular_velocity_major
        self.angular_velocity_minor = angular_velocity_minor

    def update(self, dt):
        # Actualizar los ángulos de la partícula
        self.angle_major += self.angular_velocity_major * dt
        self.angle_minor += self.angular_velocity_minor * dt

        # Asegurarnos de que los ángulos estén en el rango [0, 2π]
        self.angle_major %= 2 * np.pi
        self.angle_minor %= 2 * np.pi

    def get_position(self):
        # Convertir ángulos en coordenadas 3D en el toroide
        radius = random.uniform(TORUS_RADIUS_INNER, TORUS_RADIUS_OUTER)  # Dentro del grosor del toroide
        x = (TORUS_RADIUS_MAJOR + radius * np.cos(self.angle_minor)) * np.cos(self.angle_major) * OVAL_FACTOR_X
        y = (TORUS_RADIUS_MAJOR + radius * np.cos(self.angle_minor)) * np.sin(self.angle_major) * OVAL_FACTOR_Y
        z = radius * np.sin(self.angle_minor)
        return np.array([x, y, z])

    def draw(self):
        position = self.get_position()
        size = 0.05
        glPushMatrix()
        glTranslatef(*position)

        glDisable(GL_TEXTURE_2D)  # Deshabilitar texturas para dibujar partículas
        glColor3f(1.0, 0.5, 0.0)  # Color naranja para las partículas
        glBegin(GL_QUADS)

        # Dibujar un cubo pequeño como partícula
        vertices = [
            [-size, -size, -size], [size, -size, -size], [size, size, -size], [-size, size, -size],
            [-size, -size, size], [size, -size, size], [size, size, size], [-size, size, size]
        ]
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)
        ]
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        glEnable(GL_TEXTURE_2D)  # Volver a habilitar texturas después de dibujar partículas
        glPopMatrix()

def load_texture(texture_file):
    """Carga una textura desde un archivo y la aplica en OpenGL."""
    texture_surface = pygame.image.load(texture_file)
    texture_data = pygame.image.tostring(texture_surface, "RGB", 1)
    width, height = texture_surface.get_rect().size

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    return tex_id

def vertex_coords(theta, phi, radius):
    """Calcula las coordenadas del vértice con un factor ovalado."""
    x = (TORUS_RADIUS_MAJOR + radius * np.cos(phi)) * np.cos(theta) * OVAL_FACTOR_X
    y = (TORUS_RADIUS_MAJOR + radius * np.cos(phi)) * np.sin(theta) * OVAL_FACTOR_Y
    z = radius * np.sin(phi)
    return x, y, z

def draw_torus(texture_id_outer, texture_id_inner, hide_half):
    """Dibuja un toroide hueco con dos texturas (exterior e interior)."""
    glBindTexture(GL_TEXTURE_2D, texture_id_outer)

    glBegin(GL_QUADS)
    for i in range(NUM_SEGMENTS_MAJOR):
        for j in range(NUM_SEGMENTS_MINOR):
            # Ángulos para la posición en el toroide
            theta1 = 2 * np.pi * i / NUM_SEGMENTS_MAJOR
            theta2 = 2 * np.pi * (i + 1) / NUM_SEGMENTS_MAJOR
            phi1 = 2 * np.pi * j / NUM_SEGMENTS_MINOR
            phi2 = 2 * np.pi * (j + 1) / NUM_SEGMENTS_MINOR

            if hide_half and phi1 > np.pi:  # Ocultar mitad interna del círculo menor
                continue

            # Vértices con texturas para la parte externa
            glTexCoord2f(i / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta1, phi1, TORUS_RADIUS_OUTER))
            glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta2, phi1, TORUS_RADIUS_OUTER))
            glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta2, phi2, TORUS_RADIUS_OUTER))
            glTexCoord2f(i / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta1, phi2, TORUS_RADIUS_OUTER))

    glEnd()

def main():
    pygame.init()
    global screen
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Partículas dentro del LHC")

    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)

    # Cargar texturas
    texture_id_outer = load_texture("textura_metalica.png")
    texture_id_inner = load_texture("textura_interior.png")

    # Variables de estado
    rotate_x, rotate_y = 0, 0
    dragging = False
    hide_half = False
    zoom_level = -10.0
    particles = []

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0  # Tiempo entre cuadros en segundos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:  # Clic derecho
                dragging = True
            elif event.type == MOUSEBUTTONUP and event.button == 3:
                dragging = False
            elif event.type == MOUSEMOTION and dragging:
                rotate_x += event.rel[1]
                rotate_y += event.rel[0]
            elif event.type == KEYDOWN and event.key == K_t:  # Ocultar/mostrar mitad interna
                hide_half = not hide_half
            elif event.type == MOUSEBUTTONDOWN:  # Zoom con rueda del mouse
                if event.button == 4:  # Rueda hacia adelante
                    zoom_level += 1.0
                elif event.button == 5:  # Rueda hacia atrás
                    zoom_level -= 1.0
            elif event.type == KEYDOWN and event.key == K_i:  # Añadir partícula
                angle_major = random.uniform(0, 2 * np.pi)
                angle_minor = random.uniform(0, 2 * np.pi)
                angular_velocity_major = random.uniform(1, 3)
                angular_velocity_minor = random.uniform(-0.5, 0.5)
                particles.append(Particle(angle_major, angle_minor, angular_velocity_major, angular_velocity_minor))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        # Aplicar zoom
        glLoadIdentity()
        gluPerspective(45, (800 / 600), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom_level)

        # Aplicar rotaciones
        glPushMatrix()
        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)

        # Dibujar el toroide
        draw_torus(texture_id_outer, texture_id_inner, hide_half)

        # Dibujar partículas
        for particle in particles:
            particle.update(dt)
            particle.draw()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
