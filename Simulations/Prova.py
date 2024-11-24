from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import numpy as np

# Constantes para el anillo
TORUS_RADIUS_MAJOR = 3.0  # Radio mayor (distancia al centro del toro)
TORUS_RADIUS_OUTER = 0.8  # Radio externo (radio del tubo)
TORUS_RADIUS_INNER = 0.6  # Radio interno (grosor del tubo)
NUM_SEGMENTS_MAJOR = 64   # Divisiones alrededor del círculo mayor
NUM_SEGMENTS_MINOR = 32   # Divisiones alrededor del círculo menor

class Sphere:
    """Clase para representar una esfera que rebota dentro del anillo."""
    def __init__(self, position, velocity, radius=0.2):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.radius = radius

    def update(self, delta_time):
        """Actualiza la posición de la esfera y detecta colisiones."""
        self.position += self.velocity * delta_time

        # Rebote en los límites del toroide
        distance_to_center = np.sqrt(self.position[0]**2 + self.position[1]**2)
        if distance_to_center - self.radius < TORUS_RADIUS_MAJOR - TORUS_RADIUS_INNER or \
           distance_to_center + self.radius > TORUS_RADIUS_MAJOR + TORUS_RADIUS_OUTER:
            self.velocity[0] *= -1
            self.velocity[1] *= -1

        if abs(self.position[2]) + self.radius > TORUS_RADIUS_OUTER:
            self.velocity[2] *= -1

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

def draw_torus(texture_id_outer, texture_id_inner, hide_half):
    """Dibuja un toroide hueco con dos texturas (exterior e interior)."""
    glBindTexture(GL_TEXTURE_2D, texture_id_outer)

    glBegin(GL_QUADS)
    for i in range(NUM_SEGMENTS_MAJOR):
        for j in range(NUM_SEGMENTS_MINOR):
            theta1 = 2 * np.pi * i / NUM_SEGMENTS_MAJOR
            theta2 = 2 * np.pi * (i + 1) / NUM_SEGMENTS_MAJOR
            phi1 = 2 * np.pi * j / NUM_SEGMENTS_MINOR
            phi2 = 2 * np.pi * (j + 1) / NUM_SEGMENTS_MINOR

            if hide_half and phi1 > np.pi:  # Ocultar mitad interna del círculo menor
                continue

            def vertex_coords(theta, phi, radius):
                x = (TORUS_RADIUS_MAJOR + radius * np.cos(phi)) * np.cos(theta)
                y = (TORUS_RADIUS_MAJOR + radius * np.cos(phi)) * np.sin(theta)
                z = radius * np.sin(phi)
                return x, y, z

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

    if hide_half:
        glBindTexture(GL_TEXTURE_2D, texture_id_inner)
        glBegin(GL_QUADS)
        for i in range(NUM_SEGMENTS_MAJOR):
            for j in range(NUM_SEGMENTS_MINOR):
                theta1 = 2 * np.pi * i / NUM_SEGMENTS_MAJOR
                theta2 = 2 * np.pi * (i + 1) / NUM_SEGMENTS_MAJOR
                phi1 = 2 * np.pi * j / NUM_SEGMENTS_MINOR
                phi2 = 2 * np.pi * (j + 1) / NUM_SEGMENTS_MINOR

                if phi1 > np.pi:  # Ocultar la mitad interna
                    continue

                glTexCoord2f(i / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
                glVertex3f(*vertex_coords(theta1, phi1, TORUS_RADIUS_INNER))
                glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
                glVertex3f(*vertex_coords(theta2, phi1, TORUS_RADIUS_INNER))
                glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
                glVertex3f(*vertex_coords(theta2, phi2, TORUS_RADIUS_INNER))
                glTexCoord2f(i / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
                glVertex3f(*vertex_coords(theta1, phi2, TORUS_RADIUS_INNER))

        glEnd()

def draw_sphere(sphere):
    """Dibuja una esfera en su posición actual."""
    glPushMatrix()
    glTranslatef(*sphere.position)
    quadric = gluNewQuadric()
    gluSphere(quadric, sphere.radius, 32, 32)
    gluDeleteQuadric(quadric)
    glPopMatrix()

def main():
    pygame.init()
    global screen
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Anillo Hueco con Textura y Esferas")

    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)

    texture_id_outer = load_texture("Simulations/textura_metalica.png")
    texture_id_inner = load_texture("Simulations/textura_interior.png")

    spheres = [
        Sphere(position=[0.0, TORUS_RADIUS_MAJOR, 0.0], velocity=[0.5, 0.3, 0.2]),
        Sphere(position=[0.0, -TORUS_RADIUS_MAJOR, 0.0], velocity=[-0.4, -0.2, 0.1])
    ]

    rotate_x, rotate_y = 0, 0
    dragging = False
    hide_half = False

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                dragging = True
            elif event.type == MOUSEBUTTONUP and event.button == 3:
                dragging = False
            elif event.type == MOUSEMOTION and dragging:
                rotate_x += event.rel[1]
                rotate_y += event.rel[0]
            elif event.type == KEYDOWN and event.key == K_t:
                hide_half = not hide_half

        delta_time = clock.tick(60) / 1000.0
        for sphere in spheres:
            sphere.update(delta_time)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        glPushMatrix()
        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)

        draw_torus(texture_id_outer, texture_id_inner, hide_half)
        glDisable(GL_TEXTURE_2D)
        for sphere in spheres:
            draw_sphere(sphere)
        glEnable(GL_TEXTURE_2D)

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
