import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

# Definir la clase Particle
class Particle:
    def __init__(self, position, velocity, radius=0.02, color=(0.2, 0.8, 0.2)):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.radius = radius
        self.color = color  # Color de la partícula

# Variable para controlar si se oculta la mitad del toroide
hide_half_torus = False
slow_motion = False  # Variable para controlar el estado de cámara lenta

def draw_wireframe_torus(inner_radius=0.3, outer_radius=0.8, num_sides=30, num_rings=60):
    """Dibuja un toroide en wireframe usando ecuaciones paramétricas."""
    glColor4f(1.0, 1.0, 1.0, 0.6)  # Color blanco con opacidad
    for i in range(num_sides):
        theta = 2 * np.pi * i / num_sides
        next_theta = 2 * np.pi * (i + 1) / num_sides

        # Si está activado hide_half_torus, omitimos la mitad de las líneas
        if hide_half_torus and i < num_sides // 2:
            continue

        glBegin(GL_LINE_LOOP)
        for j in range(num_rings):
            phi = 2 * np.pi * j / num_rings
            x1 = (outer_radius + inner_radius * np.cos(theta)) * np.cos(phi)
            y1 = (outer_radius + inner_radius * np.cos(theta)) * np.sin(phi)
            z1 = inner_radius * np.sin(theta)

            x2 = (outer_radius + inner_radius * np.cos(next_theta)) * np.cos(phi)
            y2 = (outer_radius + inner_radius * np.cos(next_theta)) * np.sin(phi)
            z2 = inner_radius * np.sin(next_theta)

            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
        glEnd()

def draw_sphere(radius=0.02, slices=10, stacks=10, color=(0.2, 0.8, 0.2)):
    """Dibuja una esfera con un color específico."""
    glColor3f(*color)  # Color especificado para las partículas
    quadric = gluNewQuadric()
    gluSphere(quadric, radius, slices, stacks)

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
    global hide_half_torus, slow_motion  # Declaramos las variables como globales para modificar dentro de main
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('3D Wireframe Torus with Multiple Particles')

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
                # Agregar partícula verde con "I"
                if event.key == K_i and len(particles) < max_particles:
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
                    particles.append(Particle(position, velocity))

                # Alternar la visibilidad de la mitad del toroide con "H"
                elif event.key == K_h:
                    hide_half_torus = not hide_half_torus

                # Agregar partícula roja con "O"
                elif event.key == K_o and len(particles) < max_particles:
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
                    particles.append(Particle(position, velocity, color=(1.0, 0.0, 0.0)))  # Color rojo

                # Activar modo de cámara lenta con "K"
                elif event.key == K_k:
                    slow_motion = True

            # Desactivar cámara lenta al soltar la tecla "K"
            if event.type == KEYUP and event.key == K_k:
                slow_motion = False

        for particle in particles:
            # Ajustar velocidad de las partículas si slow_motion está activado
            velocity_scale = 0.2 if slow_motion else 1.0
            particle.position += particle.velocity * velocity_scale
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
                draw_sphere(radius=particle.radius, color=particle.color)
                glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
