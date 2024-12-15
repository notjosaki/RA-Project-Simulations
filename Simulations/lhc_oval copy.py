import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from random import uniform

# Constantes para el toroide
TORUS_RADIUS_MAJOR = 3.0
TORUS_RADIUS_OUTER = 0.3
TORUS_RADIUS_INNER = 0.2
NUM_SEGMENTS_MAJOR = 64
NUM_SEGMENTS_MINOR = 32

OVAL_FACTOR_X = 2.0
OVAL_FACTOR_Y = 1.0

class Particle:
    def __init__(self, angle, z_position, angular_velocity, z_velocity, radius, texture_id, particle_type):
        """
        Inicializa una partícula con tipo, posición angular, posición en Z y velocidades.
        """
        self.angle = angle  # Posición angular en el plano XY
        self.z_position = z_position  # Posición en Z dentro del toroide
        self.angular_velocity = angular_velocity  # Velocidad angular
        self.z_velocity = z_velocity  # Velocidad en Z
        self.radius = radius  # Radio de la partícula
        self.texture_id = texture_id  # Textura asociada
        self.type = particle_type  # Tipo de partícula (lepton, neutron, etc.)

    def update(self, torus_radius_major, torus_radius_inner):
        """
        Actualiza la posición de la partícula.
        """
        self.angle += self.angular_velocity
        if self.angle > 2 * np.pi:  # Mantener ángulo en rango [0, 2π]
            self.angle -= 2 * np.pi

        # Rebote en Z
        self.z_position += self.z_velocity
        if abs(self.z_position) > torus_radius_inner:
            self.z_velocity *= -1

    def draw(self):
        """
        Dibuja la partícula con su textura en la posición actual.
        """
        x = TORUS_RADIUS_MAJOR * np.cos(self.angle) * OVAL_FACTOR_X
        y = TORUS_RADIUS_MAJOR * np.sin(self.angle) * OVAL_FACTOR_Y
        z = self.z_position

        glPushMatrix()
        glTranslatef(x, y, z)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.radius, 16, 16)
        gluDeleteQuadric(quadric)

        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

def check_collision_and_interact(p1, p2, particles, textures):
    """
    Detecta y maneja colisiones entre partículas con interacciones específicas.
    """
    # Calcular distancia entre partículas
    x1 = TORUS_RADIUS_MAJOR * np.cos(p1.angle) * OVAL_FACTOR_X
    y1 = TORUS_RADIUS_MAJOR * np.sin(p1.angle) * OVAL_FACTOR_Y
    z1 = p1.z_position

    x2 = TORUS_RADIUS_MAJOR * np.cos(p2.angle) * OVAL_FACTOR_X
    y2 = TORUS_RADIUS_MAJOR * np.sin(p2.angle) * OVAL_FACTOR_Y
    z2 = p2.z_position

    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

    if distance < (p1.radius + p2.radius):
        # Lepton + Boson → Desintegración
        if p1.type == "lepton" and p2.type == "boson" or p2.type == "lepton" and p1.type == "boson":
            particles.remove(p1)
            particles.remove(p2)
            for _ in range(3):
                new_particle = Particle(
                    angle=p1.angle, z_position=p1.z_position,
                    angular_velocity=np.random.uniform(0.01, 0.05),
                    z_velocity=np.random.uniform(-0.02, 0.02),
                    radius=0.02, texture_id=textures['neutron'], particle_type="neutron"
                )
                particles.append(new_particle)

        # Proton + Quark → Fusión en Higgs
        elif (p1.type == "proton" and p2.type == "quark") or (p1.type == "quark" and p2.type == "proton"):
            p1.texture_id = textures['higgs']
            p1.type = "higgs"
            particles.remove(p2)

        # Neutron → Repulsión
        elif p1.type == "neutron" or p2.type == "neutron":
            p1.z_velocity *= -1
            p2.z_velocity *= -1

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
    """Dibuja un toroide con texturas diferentes para el exterior y el interior."""
    
    # Dibujar la superficie exterior del toroide
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

            # Exterior
            glTexCoord2f(i / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta1, phi1, TORUS_RADIUS_OUTER))
            glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta2, phi1, TORUS_RADIUS_OUTER))
            glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta2, phi2, TORUS_RADIUS_OUTER))
            glTexCoord2f(i / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta1, phi2, TORUS_RADIUS_OUTER))
    glEnd()

    # Dibujar la superficie interior del toroide
    glBindTexture(GL_TEXTURE_2D, texture_id_inner)
    glBegin(GL_QUADS)
    for i in range(NUM_SEGMENTS_MAJOR):
        for j in range(NUM_SEGMENTS_MINOR):
            theta1 = 2 * np.pi * i / NUM_SEGMENTS_MAJOR
            theta2 = 2 * np.pi * (i + 1) / NUM_SEGMENTS_MAJOR
            phi1 = 2 * np.pi * j / NUM_SEGMENTS_MINOR
            phi2 = 2 * np.pi * (j + 1) / NUM_SEGMENTS_MINOR

            if hide_half and phi1 > np.pi:
                continue

            # Interior
            glTexCoord2f(i / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta1, phi1, TORUS_RADIUS_INNER))
            glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, j / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta2, phi1, TORUS_RADIUS_INNER))
            glTexCoord2f((i + 1) / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta2, phi2, TORUS_RADIUS_INNER))
            glTexCoord2f(i / NUM_SEGMENTS_MAJOR, (j + 1) / NUM_SEGMENTS_MINOR)
            glVertex3f(*vertex_coords(theta1, phi2, TORUS_RADIUS_INNER))
    glEnd()

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("LHC: Partículas Interactivas")

    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -12)

    textures = {
        'lepton': load_texture("lepton.png"),
        'neutron': load_texture("neutron.png"),
        'proton': load_texture("proton.png"),
        'quark': load_texture("quark.png"),
        'boson': load_texture("boson.png"),
        'higgs': load_texture("higgs.png"),
    }

    particles = []
    current_view = 0
    camera_views = [
        (0, 0, 0), (90, 0, 0), (-90, 0, 0), (0, 90, 0), (0, -90, 0), (0, 180, 0)
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_l:  # Lepton
                    particles.append(Particle(0, 0, 0.02, 0.01, 0.05, textures['lepton'], "lepton"))
                elif event.key == K_p:  # Proton
                    particles.append(Particle(0, 0, 0.01, -0.01, 0.05, textures['proton'], "proton"))
                elif event.key == K_q:  # Quark
                    particles.append(Particle(0, 0, -0.02, 0.01, 0.05, textures['quark'], "quark"))
                elif event.key == K_b:  # Boson
                    particles.append(Particle(0, 0, 0.03, 0.02, 0.05, textures['boson'], "boson"))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        rotate_x, rotate_y, rotate_z = camera_views[current_view]
        glLoadIdentity()
        gluPerspective(45, (800 / 600), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -12)
        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)
        glRotatef(rotate_z, 0, 0, 1)

        draw_torus(textures['proton'], textures['quark'], False)

        for i, p1 in enumerate(particles):
            for j in range(i + 1, len(particles)):
                check_collision_and_interact(p1, particles[j], particles, textures)
            p1.update(TORUS_RADIUS_MAJOR, TORUS_RADIUS_INNER)
            p1.draw()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()