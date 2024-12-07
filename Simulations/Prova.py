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
    def __init__(self, position, texture_id, velocity=None, radius=0.05):
        self.position = np.array(position, dtype=float)
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius
        self.texture_id = texture_id

    def update(self):
        self.position += self.velocity

        # Mantener la partícula dentro del anillo ovalado
        r = np.sqrt(self.position[0]**2 / OVAL_FACTOR_X**2 + self.position[1]**2 / OVAL_FACTOR_Y**2)
        if r > TORUS_RADIUS_MAJOR - self.radius:
            self.velocity[:2] = -self.velocity[:2]  # Rebotar en los ejes X e Y

        # Rebote en los límites Z
        if self.position[2] + self.radius > TORUS_RADIUS_OUTER or self.position[2] - self.radius < -TORUS_RADIUS_OUTER:
            self.velocity[2] = -self.velocity[2]

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glEnable(GL_TEXTURE_2D)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.radius, 20, 20)
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()


def load_texture(texture_file):
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
    x = (TORUS_RADIUS_MAJOR + radius * np.cos(phi)) * np.cos(theta) * OVAL_FACTOR_X
    y = (TORUS_RADIUS_MAJOR + radius * np.cos(phi)) * np.sin(theta) * OVAL_FACTOR_Y
    z = radius * np.sin(phi)
    return x, y, z


def draw_torus(texture_id_outer, texture_id_inner, hide_half):
    glBindTexture(GL_TEXTURE_2D, texture_id_outer)
    glBegin(GL_QUADS)
    for i in range(NUM_SEGMENTS_MAJOR):
        for j in range(NUM_SEGMENTS_MINOR):
            theta1 = 2 * np.pi * i / NUM_SEGMENTS_MAJOR
            theta2 = 2 * np.pi * (i + 1) / NUM_SEGMENTS_MAJOR
            phi1 = 2 * np.pi * j / NUM_SEGMENTS_MINOR
            phi2 = 2 * np.pi * (j + 1) / NUM_SEGMENTS_MINOR

            if hide_half and phi1 > np.pi:
                continue

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
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("LHC con partículas en un anillo ovalado")

    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)

    texture_id_outer = load_texture("Simulations/Imatges/textura_metalica.png")
    texture_id_inner = load_texture("Simulations/Imatges/textura_interior.png")
    particle_texture = load_texture("Simulations/Imatges/textura-roja.png")

    spheres = [
        Particle(position=(np.random.uniform(-2, 2), np.random.uniform(-2, 2), np.random.uniform(-0.2, 0.2)),
                 texture_id=particle_texture) for _ in range(10)
    ]

    rotate_x, rotate_y = 0, 0
    dragging = False
    hide_half = False
    zoom_level = -10.0

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
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom_level += 1.0
                elif event.button == 5:
                    zoom_level -= 1.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        glLoadIdentity()
        gluPerspective(45, (800 / 600), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom_level)

        glPushMatrix()
        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)
        draw_torus(texture_id_outer, texture_id_inner, hide_half)
        glPopMatrix()

        for sphere in spheres:
            sphere.update()
            sphere.draw()

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    main()
