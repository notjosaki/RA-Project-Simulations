import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

# Definir la clase Particle
class Particle:
    def __init__(self, position, velocity, radius=0.02, color=(0.2, 0.8, 0.2), texture=None):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.radius = radius
        self.color = color  # Color de la partícula (verde o azul)
        self.texture = texture  # Textura de la partícula

# Variable para controlar si se oculta la mitad del toroide
hide_half_torus = False

def load_texture(path):
    """Carga una textura desde un archivo y la prepara para OpenGL."""
    texture_surface = pygame.image.load(path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width, height = texture_surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id

def draw_textured_sphere(radius=0.02, slices=10, stacks=10, texture=None):
    """Dibuja una esfera con textura."""
    if texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
    else:
        glDisable(GL_TEXTURE_2D)

    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluSphere(quadric, radius, slices, stacks)

    if texture:
        glDisable(GL_TEXTURE_2D)

def setup_view(x_offset, y_offset, angle_x, angle_y, zoom):
    """Configura cada perspectiva de la cámara."""
    glViewport(x_offset, y_offset, 400, 400)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(zoom, zoom, zoom, 0, 0, 0, 0, 1, 0)
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)

def reflect_velocity(position, velocity, R=0.8, r=0.3):
    """Refleja la velocidad de la partícula al colisionar con las paredes del toroide."""
    x, y, z = position
    distance = np.sqrt(x**2 + y**2)
    F = (distance - R)**2 + z**2 - r**2
    if F > 0:
        dF_dx = 2 * (distance - R) * (x / distance)
        dF_dy = 2 * (distance - R) * (y / distance)
        dF_dz = 2 * z
        normal = np.array([dF_dx, dF_dy, dF_dz])
        normal = normal / np.linalg.norm(normal)
        velocity_reflected = velocity - 2 * np.dot(velocity, normal) * normal
        return velocity_reflected
    return velocity

def main():
    global hide_half_torus  # Declaramos la variable como global para modificarla dentro de main
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('3D Textured Particles in Torus')

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    clock = pygame.time.Clock()
    zoom = 3.0

    particles = []
    max_particles = 100
    torus_inner_radius = 0.3
    torus_outer_radius = 0.8
    R = torus_outer_radius
    r = torus_inner_radius
    slowdown_factor = 0.5  # Factor de ralentización de velocidad

    # Cargar texturas
    texture_red = load_texture('C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/Imatges/textura-roja.png')
    texture_blue = load_texture('C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/Imatges/textura-azul.png')

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom -= 0.1
                elif event.button == 5:
                    zoom += 0.1
            if event.type == KEYDOWN:
                if event.key == K_i:
                    if len(particles) < max_particles:
                        theta = random.uniform(0, 2 * np.pi)
                        phi = random.uniform(0, 2 * np.pi)
                        local_r = random.uniform(-r + 0.02, r - 0.02)
                        x = (R + local_r * np.cos(phi)) * np.cos(theta)
                        y = (R + local_r * np.cos(phi)) * np.sin(theta)
                        z = local_r * np.sin(phi)
                        position = [x, y, z]
                        tangent_theta = np.array([-np.sin(theta), np.cos(theta), 0])
                        tangent_phi = np.array([-np.cos(theta) * np.cos(phi), -np.sin(theta) * np.cos(phi), np.sin(phi)])
                        velocity = tangent_theta * random.uniform(0.01, 0.03) + tangent_phi * random.uniform(0.01, 0.03)
                        # Partícula verde con textura roja
                        particles.append(Particle(position, velocity, texture=texture_red))
                elif event.key == K_h:
                    hide_half_torus = not hide_half_torus
                elif event.key == K_o:
                    if len(particles) < max_particles:
                        theta = random.uniform(0, 2 * np.pi)
                        phi = random.uniform(0, 2 * np.pi)
                        local_r = random.uniform(-r + 0.02, r - 0.02)
                        x = (R + local_r * np.cos(phi)) * np.cos(theta)
                        y = (R + local_r * np.cos(phi)) * np.sin(theta)
                        z = local_r * np.sin(phi)
                        position = [x, y, z]
                        tangent_theta = np.array([-np.sin(theta), np.cos(theta), 0])
                        tangent_phi = np.array([-np.cos(theta) * np.cos(phi), -np.sin(theta) * np.cos(phi), np.sin(phi)])
                        velocity = tangent_theta * random.uniform(0.01, 0.03) + tangent_phi * random.uniform(0.01, 0.03)
                        # Partícula azul con textura azul
                        particles.append(Particle(position, velocity, color=(0.2, 0.2, 1.0), texture=texture_blue))
                elif event.key == K_k:
                    for particle in particles:
                        particle.velocity *= slowdown_factor

        for particle in particles:
            particle.position += particle.velocity
            particle.velocity = reflect_velocity(particle.position, particle.velocity, R, r)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for x_offset, y_offset, angle_x, angle_y in [
            (0, 400, 0, 0),
            (400, 400, 0, 90),
            (0, 0, 90, 0),
            (400, 0, 30, 45)
        ]:
            setup_view(x_offset, y_offset, angle_x, angle_y, zoom)
            draw_wireframe_torus(inner_radius=torus_inner_radius, outer_radius=torus_outer_radius)
            for particle in particles:
                glPushMatrix()
                glTranslatef(*particle.position)
                draw_textured_sphere(radius=particle.radius, texture=particle.texture)
                glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()


