import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from random import uniform
import time
from random import uniform, choice
import pandas as pd
import os

# Constantes para el toroide
TORUS_RADIUS_MAJOR = 3.0
TORUS_RADIUS_OUTER = 0.3
TORUS_RADIUS_INNER = 0.2
NUM_SEGMENTS_MAJOR = 64
NUM_SEGMENTS_MINOR = 32

OVAL_FACTOR_X = 2.0
OVAL_FACTOR_Y = 1.0

collision_log = []  # Lista global para registrar colisiones


class Particle:
    def __init__(self, angle, z_position, angular_velocity, z_velocity, radius, texture_id=None, particle_type=None):
        """
        Inicializa una partícula con posición angular, en el eje Z, textura y tipo.
        """
        self.angle = angle
        self.z_position = z_position
        self.angular_velocity = angular_velocity
        self.z_velocity = z_velocity
        self.radius = radius
        self.texture_id = texture_id
        self.particle_type = particle_type  # Tipo de partícula (lepton, boson, quark, proton, neutron)

    def update(self, torus_radius_major, torus_radius_inner):
        """
        Actualiza la posición de la partícula siguiendo el patrón del tubo.
        """
        # Actualizar ángulo para movimiento orbital
        self.angle += self.angular_velocity
        if self.angle > 2 * np.pi:  # Mantener ángulo en el rango [0, 2π]
            self.angle -= 2 * np.pi

        # Actualizar posición en el eje Z
        self.z_position += self.z_velocity
        if abs(self.z_position) > torus_radius_inner:  # Rebote en las paredes del tubo
            self.z_velocity *= -1

    def draw(self):
        """
        Dibuja la partícula en su posición actual calculada a partir del ángulo y Z.
        """
        x = TORUS_RADIUS_MAJOR * np.cos(self.angle) * OVAL_FACTOR_X
        y = TORUS_RADIUS_MAJOR * np.sin(self.angle) * OVAL_FACTOR_Y
        z = self.z_position

        glPushMatrix()
        glTranslatef(x, y, z)

        if self.texture_id:
            # Si tiene textura, aplícala
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            quad = gluNewQuadric()
            gluQuadricTexture(quad, GL_TRUE)
            gluSphere(quad, self.radius, 16, 16)
            gluDeleteQuadric(quad)
            glDisable(GL_TEXTURE_2D)
        else:
            # Dibujar sin textura
            quad = gluNewQuadric()
            gluSphere(quad, self.radius, 16, 16)
            gluDeleteQuadric(quad)

        glPopMatrix()

    def check_collision(self, other_particle, particles, particles_to_remove, texture_neutron):
        global collision_log
        # Lógica para detectar colisiones
        x1 = TORUS_RADIUS_MAJOR * np.cos(self.angle) * OVAL_FACTOR_X
        y1 = TORUS_RADIUS_MAJOR * np.sin(self.angle) * OVAL_FACTOR_Y
        z1 = self.z_position

        x2 = TORUS_RADIUS_MAJOR * np.cos(other_particle.angle) * OVAL_FACTOR_X
        y2 = TORUS_RADIUS_MAJOR * np.sin(other_particle.angle) * OVAL_FACTOR_Y
        z2 = other_particle.z_position

        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

        if distance < self.radius + other_particle.radius:
            # Registrar la colisión entre tipos
            collision_log.append(f"{self.particle_type} + {other_particle.particle_type}")

            # Reglas especiales de colisión
            if (self.particle_type == "lepton" and other_particle.particle_type == "boson") or \
            (self.particle_type == "boson" and other_particle.particle_type == "lepton"):
                collision_log.append("Lepton + Boson -> 3 Neutrones")
                particles_to_remove.update([self, other_particle])  # Marcar para eliminación
                for _ in range(3):
                    particles.append(Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.01, 0.05),
                        z_velocity=uniform(-0.02, 0.02),
                        radius=0.05,
                        texture_id=texture_neutron,
                        particle_type="neutron"
                    ))

            elif self.particle_type == "proton" and other_particle.particle_type == "quark":
                collision_log.append("Proton + Quark -> Higgs")
                self.particle_type = "higgs"
                self.texture_id = textura_higgs
                particles_to_remove.add(other_particle)  # Marcar quark para eliminación

            elif self.particle_type == "neutron" or other_particle.particle_type == "neutron":
                collision_log.append("Neutron + Any -> Repulsion")
                self.z_velocity, other_particle.z_velocity = other_particle.z_velocity, self.z_velocity



            elif self.particle_type == "quark" and other_particle.particle_type == "proton":
                collision_log.append("Proton + Quark -> Higgs")
                other_particle.particle_type = "higgs"
                other_particle.texture_id = textura_higgs
                particles.remove(self)


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


# Menú principal
def menu():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont("Arial", 36)
    choice = None

    while choice is None:
        screen.fill((0, 0, 0))
        text1 = font.render("1: Simulación Creativa", True, (255, 255, 255))
        text2 = font.render("2: Simulación Programada", True, (255, 255, 255))
        screen.blit(text1, (200, 200))
        screen.blit(text2, (200, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_1:
                    choice = "creative"
                elif event.key == K_2:
                    choice = "programmed"

    return choice

# Simulación Programada
def programmed_simulation(particles, textures, duration=60):
    """
    Ejecuta la simulación programada durante un tiempo específico.
    """
    start_time = time.time()
    last_particle_time = start_time

    while time.time() - start_time < duration:
        current_time = time.time()

        # Añadir partículas cada segundo
        if current_time - last_particle_time >= 1:
            particle_type = choice(["lepton", "boson", "proton", "quark", "neutron"])
            texture = textures[particle_type]
            new_particle = Particle(
                angle=uniform(0, 2 * np.pi),
                z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                angular_velocity=uniform(0.01, 0.05),
                z_velocity=uniform(-0.02, 0.02),
                radius=0.05,
                texture_id=texture,
                particle_type=particle_type
            )
            particles.append(new_particle)
            last_particle_time = current_time

        # Crear un conjunto para eliminar partículas de manera segura
        particles_to_remove = set()

        # Renderizar la simulación
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # Dibujar y actualizar partículas
        particles_copy = particles[:]  # Copia segura de la lista
        for i, particle in enumerate(particles_copy):
            for j in range(i + 1, len(particles_copy)):
                if particle in particles_to_remove or particles_copy[j] in particles_to_remove:
                    continue  # Saltar si alguna partícula está marcada para eliminar
                particle.check_collision(particles_copy[j], particles, particles_to_remove, textures["neutron"])
            particle.update(TORUS_RADIUS_MAJOR, TORUS_RADIUS_INNER)
            particle.draw()

        # Eliminar las partículas marcadas
        particles = [p for p in particles if p not in particles_to_remove]

        pygame.display.flip()
        pygame.time.wait(10)

    # Guardar los datos al finalizar la simulación
    export_to_excel()


# Exportar datos a Excel
def export_to_excel():
    global collision_log
    if collision_log:
        # Eliminar el archivo si ya existe
        if os.path.exists("collision_analysis.xlsx"):
            os.remove("collision_analysis.xlsx")

        # Crear el archivo Excel con los datos
        total_collisions = len(collision_log)
        colisiones_agrupadas = pd.Series(collision_log).value_counts().reset_index()
        colisiones_agrupadas.columns = ["Tipo de Colisión", "Cantidad"]

        with pd.ExcelWriter("collision_analysis.xlsx", mode="w") as writer:
            colisiones_agrupadas.to_excel(writer, sheet_name="Resumen", index=False)
            summary = pd.DataFrame({"Total de Colisiones": [total_collisions]})
            summary.to_excel(writer, sheet_name="Total", index=False)

        print("Archivo Excel guardado: collision_analysis.xlsx")
    else:
        print("No hay colisiones registradas para exportar.")



def main():

    choice = menu()
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -12)

    global textura_higgs, textura_neutron
    textura_lepton = load_texture("lepton.png")
    textura_higgs = load_texture("higgs.png")
    textura_quark = load_texture("quark.png")
    textura_boson = load_texture("boson.png")
    textura_proton = load_texture("proton.png")
    textura_neutron = load_texture("neutron.png")
    texture_id_outer = load_texture("textura_metalica.png")
    texture_id_inner = load_texture("textura_interior.png")

    textures = {
        "lepton": textura_lepton,
        "higgs": textura_higgs,
        "quark": textura_quark,
        "boson": textura_boson,
        "proton": textura_proton,
        "neutron": textura_neutron
    }

    particles = []

    if choice == "programmed":
        programmed_simulation(particles, textures)
        pygame.quit()
        return


    hide_half = False
    zoom_level = -12.0
    particles = []

    # Vistas predefinidas
    camera_views = [
        (0, 0, 0),     # Vista inicial
        (90, 0, 0),    # Vista desde arriba
        (-90, 0, 0),   # Vista desde abajo
        (0, 90, 0),    # Vista lateral derecha
        (0, -90, 0),   # Vista lateral izquierda
        (0, 180, 0),   # Vista trasera
    ]
    current_view = 0  # Índice de la vista actual

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_t:
                    hide_half = not hide_half
                elif event.key == K_f:
                    current_view = (current_view + 1) % len(camera_views)
                elif event.key == K_i:
                    # Generar partícula estándar
                    new_particle = Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.01, 0.05),
                        z_velocity=uniform(-0.02, 0.02),
                        radius=0.05
                    )
                    particles.append(new_particle)
                elif event.key == K_o:
                    new_particle_outer = Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.01, 0.05),
                        z_velocity=uniform(-0.02, 0.02),
                        radius=0.05,
                        texture_id=textura_neutron,
                        particle_type="neutron"
                    )
                    particles.append(new_particle_outer)
                elif event.key == K_l:  # Tecla L para leptones
                    new_lepton = Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.02, 0.06),
                        z_velocity=uniform(-0.03, 0.03),
                        radius=0.06,
                        texture_id=textura_lepton,
                        particle_type="lepton"
                    )
                    particles.append(new_lepton)
                elif event.key == K_h:  # Tecla H para Higgs
                    new_higgs = Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.01, 0.04),
                        z_velocity=uniform(-0.01, 0.02),
                        radius=0.08,
                        texture_id=textura_higgs,
                        particle_type="higgs"
                    )
                    particles.append(new_higgs)
                elif event.key == K_q:  # Tecla Q para quarks
                    new_quark = Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.03, 0.07),
                        z_velocity=uniform(-0.04, 0.04),
                        radius=0.05,
                        texture_id=textura_quark,
                        particle_type="quark"
                    )
                    particles.append(new_quark)
                elif event.key == K_b:  # Tecla B para bosones
                    new_boson = Particle(
                        angle=uniform(0, 2 * np.pi),
                        z_position=uniform(-TORUS_RADIUS_INNER, TORUS_RADIUS_INNER),
                        angular_velocity=uniform(0.015, 0.045),
                        z_velocity=uniform(-0.02, 0.02),
                        radius=0.07,
                        texture_id=textura_boson,
                        particle_type="boson"
                    )
                    particles.append(new_boson)
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

        # Aplicar las rotaciones de la cámara
        rotate_x, rotate_y, rotate_z = camera_views[current_view]
        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)
        glRotatef(rotate_z, 0, 0, 1)

        # Dibujar el toroide
        draw_torus(texture_id_outer, texture_id_inner, hide_half)

        # Actualizar y dibujar partículas
        glDisable(GL_TEXTURE_2D)

        for i, particle in enumerate(particles):
            for j in range(i + 1, len(particles)):
                particle.check_collision(particles[j], particles, textura_neutron)
            particle.update(TORUS_RADIUS_MAJOR, TORUS_RADIUS_INNER)
            particle.draw()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

