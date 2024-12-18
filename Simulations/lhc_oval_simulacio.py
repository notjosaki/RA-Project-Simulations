import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from random import uniform
import pandas as pd

# Constantes para el toroide
TORUS_RADIUS_MAJOR = 3.0
TORUS_RADIUS_OUTER = 0.3
TORUS_RADIUS_INNER = 0.2
NUM_SEGMENTS_MAJOR = 64
NUM_SEGMENTS_MINOR = 32

OVAL_FACTOR_X = 2.0
OVAL_FACTOR_Y = 1.0

# Diccionario para registrar las colisiones
collision_log = {}

def register_collision(p1, p2):
    pair = tuple(sorted([p1.particle_type, p2.particle_type]))
    impact_energy = 0.5 * p1.radius * (p1.angular_velocity**2 + p1.z_velocity**2) + \
                    0.5 * p2.radius * (p2.angular_velocity**2 + p2.z_velocity**2)

    if pair in collision_log:
        count, total_energy, first_impact_energy, _ = collision_log[pair]
        collision_log[pair] = (
            count + 1,  # Incrementar el contador
            total_energy + impact_energy,  # Sumar energía de impacto
            first_impact_energy,  # Mantener el primer impacto
            impact_energy  # Actualizar la última energía de impacto
        )
    else:
        collision_log[pair] = (
            1,  # Primera colisión
            impact_energy,  # Energía acumulada
            impact_energy,  # Primera energía de impacto
            impact_energy  # Última energía de impacto
        )

class Particle:
    def __init__(self, angle, z_position, angular_velocity, z_velocity, radius, texture_id, particle_type):
        self.angle = angle
        self.z_position = z_position
        self.angular_velocity = angular_velocity
        self.z_velocity = z_velocity
        self.radius = radius
        self.texture_id = texture_id
        self.particle_type = particle_type

    def update(self, torus_radius_major, torus_radius_inner):
        self.angle += self.angular_velocity
        if self.angle > 2 * np.pi:
            self.angle -= 2 * np.pi

        self.z_position += self.z_velocity
        if abs(self.z_position) > torus_radius_inner:
            self.z_velocity *= -1

    def draw(self):
        x = TORUS_RADIUS_MAJOR * np.cos(self.angle) * OVAL_FACTOR_X
        y = TORUS_RADIUS_MAJOR * np.sin(self.angle) * OVAL_FACTOR_Y
        z = self.z_position

        glPushMatrix()
        glTranslatef(x, y, z)

        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            quad = gluNewQuadric()
            gluQuadricTexture(quad, GL_TRUE)
            gluSphere(quad, self.radius, 16, 16)
            gluDeleteQuadric(quad)
            glDisable(GL_TEXTURE_2D)
        else:
            quad = gluNewQuadric()
            gluSphere(quad, self.radius, 16, 16)
            gluDeleteQuadric(quad)

        glPopMatrix()

    def check_collision(self, other_particle, particles, texture_neutron):
        x1 = TORUS_RADIUS_MAJOR * np.cos(self.angle) * OVAL_FACTOR_X
        y1 = TORUS_RADIUS_MAJOR * np.sin(self.angle) * OVAL_FACTOR_Y
        z1 = self.z_position

        x2 = TORUS_RADIUS_MAJOR * np.cos(other_particle.angle) * OVAL_FACTOR_X
        y2 = TORUS_RADIUS_MAJOR * np.sin(other_particle.angle) * OVAL_FACTOR_Y
        z2 = other_particle.z_position

        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

        if distance < self.radius + other_particle.radius:
            register_collision(self, other_particle)

            # Colisiones especiales
            textura_higgs = load_texture("higgs.png")
            if (self.particle_type == "Lepton" and other_particle.particle_type == "Boson") or \
               (self.particle_type == "Boson" and other_particle.particle_type == "Lepton"):
                if self in particles: particles.remove(self)
                if other_particle in particles: particles.remove(other_particle)
                for _ in range(3):
                    particles.append(Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.01, 0.05),
                        z_velocity=uniform(-0.02, 0.02),
                        radius=0.05,
                        texture_id=texture_neutron,
                        particle_type="Neutron"
                    ))
            elif self.particle_type == "Proton" and other_particle.particle_type == "Quark":
                self.particle_type = "Higgs"
                self.texture_id = textura_higgs
                if other_particle in particles: particles.remove(other_particle)
            elif self.particle_type == "Quark" and other_particle.particle_type == "Proton":
                other_particle.particle_type = "Higgs"
                other_particle.texture_id = textura_higgs
                if self in particles: particles.remove(self)
            elif self.particle_type == "Neutron" or other_particle.particle_type == "Neutron":
                self.z_velocity, other_particle.z_velocity = other_particle.z_velocity, self.z_velocity
                self.angular_velocity, other_particle.angular_velocity = other_particle.angular_velocity, self.angular_velocity


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

def initialize_particles(textures):
    particles = []

    print("Introduce las cantidades iniciales de cada tipo de partícula:")
    counts = {
        "Proton": int(input("Protones: ")),
        "Neutron": int(input("Neutrones: ")),
        "Lepton": int(input("Leptones: ")),
        "Higgs": int(input("Higgs: ")),
        "Quark": int(input("Quarks: ")),
        "Boson": int(input("Bosones: "))
    }

    for particle_type, count in counts.items():
        for _ in range(count):
            particles.append(Particle(
                angle=uniform(0, 2 * np.pi),
                z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                angular_velocity=uniform(0.01, 0.05),
                z_velocity=uniform(-0.02, 0.02),
                radius=0.05 if particle_type not in ["Higgs"] else 0.08,
                texture_id=textures[particle_type],
                particle_type=particle_type
            ))

    return particles

def export_to_excel():
    collision_data = [
        (
            key[0],  # Partícula 1
            key[1],  # Partícula 2
            count,   # Número de colisiones
            total_energy,  # Energía acumulada
            first_impact_energy,  # Primera energía de impacto
            last_impact_energy  # Última energía de impacto
        )
        for key, (count, total_energy, first_impact_energy, last_impact_energy) in collision_log.items()
    ]

    df = pd.DataFrame(
        collision_data,
        columns=["Partícula 1", "Partícula 2", "Colisiones", "Energía acumulada", "Primera energía de impacto", "Última energía de impacto"]
    )

    filename = input("Introduce el nombre del archivo Excel para guardar los datos de la simulación: ")
    if not filename.endswith(".xlsx"):
        filename += ".xlsx"

    df.to_excel(filename, index=False)
    print(f"Datos exportados a {filename}")

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
    pygame.display.set_caption("Acelerador de partículas con colisiones")

    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -12)

    textures = {
        "Proton": load_texture("proton.png"),
        "Neutron": load_texture("neutron.png"),
        "Lepton": load_texture("lepton.png"),
        "Higgs": load_texture("higgs.png"),
        "Quark": load_texture("quark.png"),
        "Boson": load_texture("boson.png"),
        "textura_metalica" : load_texture("textura_metalica.png"),
        "textura_interior" : load_texture("textura_interior.png")
    }

    particles = initialize_particles(textures)
    zoom_level = -12.0
    hide_half = False

    camera_views = [
        (0, 0, 0),     # Vista inicial
        (90, 0, 0),    # Vista desde arriba
        (-90, 0, 0),   # Vista desde abajo
        (0, 90, 0),    # Vista lateral derecha
        (0, -90, 0),   # Vista lateral izquierda
        (0, 180, 0),   # Vista trasera
    ]
    current_view = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                export_to_excel()
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_t:
                    hide_half = not hide_half
                elif event.key == K_f:
                    current_view = (current_view + 1) % len(camera_views)
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

        rotate_x, rotate_y, rotate_z = camera_views[current_view]
        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)
        glRotatef(rotate_z, 0, 0, 1)

        draw_torus(textures["textura_metalica"], textures["textura_interior"], hide_half)

        particles_copy = particles[:]
        for i, particle in enumerate(particles_copy):
            for j in range(i + 1, len(particles_copy)):
                particle.check_collision(particles_copy[j], particles, textures["Neutron"])

            particle.update(TORUS_RADIUS_MAJOR, TORUS_RADIUS_INNER)
            particle.draw()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
