import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

# Definir los vértices y las aristas del cubo
vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

def load_texture(image_path):
    texture_surface = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_rect().size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id

# Clase para representar partículas usando gluSphere
class Particle:
    def __init__(self, position, velocity, color, lifetime=1.0):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.color = color
        self.lifetime = lifetime  # Duración en segundos

    def update(self, delta_time):
        self.position += self.velocity * delta_time
        self.lifetime -= delta_time

    def draw(self):
        glColor3fv(self.color)
        glPushMatrix()
        glTranslatef(*self.position)
        
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, 0.02, 10, 10)  # Partícula pequeña

        glPopMatrix()

# Modificar la clase Sphere para detectar colisiones
class Sphere:
    def __init__(self, position, texture_id, velocity=None, radius=0.05, color=None):
        self.position = np.array(position, dtype=float)
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius
        self.texture_id = texture_id
        self.color = color  # Guardar color para detección de colisión

    def update(self, speed_factor):
        self.position += self.velocity * speed_factor
        for i in range(3):  # Para x, y, z
            if self.position[i] + self.radius > 1 or self.position[i] - self.radius < -1:
                self.velocity[i] = -self.velocity[i]

    def draw(self):
        slices = 20
        stacks = 20
        glPushMatrix()
        glTranslatef(*self.position)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, self.radius, slices, stacks)

        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def check_collision(self, other):
        distance = np.linalg.norm(self.position - other.position)
        return distance < (self.radius + other.radius) and self.color != other.color

def draw_cube():
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def setup_view(x_offset, y_offset, angle_x, angle_y, zoom):
    glViewport(x_offset, y_offset, 400, 400)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(zoom, zoom, zoom, 0, 0, 0, 0, 1, 0)
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Cubo 3D con Esferas Texturizadas')

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Cargar texturas
    texture_red = load_texture('C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/Imatges/textura-roja.png')
    texture_blue = load_texture('C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/Imatges/textura-azul.png')

    spheres = []
    particles = []  # Lista para almacenar partículas
    clock = pygame.time.Clock()

    speed_factor = 1.0  # Factor de velocidad
    zoom = 3.0  # Posición inicial de zoom

    while True:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_i:
                    x, y, z = random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9)
                    spheres.append(Sphere((x, y, z), texture_id=texture_red, color=(1, 0, 0)))
                elif event.key == K_o:
                    x, y, z = random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9)
                    spheres.append(Sphere((x, y, z), texture_id=texture_blue, color=(0, 0, 1)))
                elif event.key == K_k:  # Tecla K para reducir la velocidad
                    speed_factor = 0.3  # Reducir la velocidad
            if event.type == KEYUP:
                if event.key == K_k:  # Si se suelta la tecla K, volver a la velocidad normal
                    speed_factor = 1.0

            # Manejo de la rueda del ratón para hacer zoom
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda hacia arriba
                    zoom -= 0.1  # Acercar (zoom in)
                elif event.button == 5:  # Rueda hacia abajo
                    zoom += 0.1  # Alejar (zoom out)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Dibujar vistas
        for x_offset, y_offset, angle_x, angle_y in [(0, 400, 0, 0), (400, 400, 0, 90), (0, 0, 90, 0), (400, 0, 30, 45)]:
            setup_view(x_offset, y_offset, angle_x, angle_y, zoom)
            draw_cube()

            # Actualizar y dibujar esferas
            for sphere in spheres[:]:
                sphere.update(speed_factor)
                sphere.draw()

            # Verificar colisiones entre esferas
            for i, sphere1 in enumerate(spheres):
                for j, sphere2 in enumerate(spheres[i+1:], i+1):
                    if sphere1.check_collision(sphere2):
                        collision_position = (sphere1.position + sphere2.position) / 2
                        for _ in range(20):
                            velocity = np.random.uniform(-0.05, 0.05, 3)
                            particles.append(Particle(collision_position, velocity, color=(1, 1, 1)))  # Color blanco
                        spheres.remove(sphere1)
                        spheres.remove(sphere2)
                        break

            # Actualizar y dibujar partículas
            for particle in particles[:]:
                particle.update(delta_time)
                if particle.lifetime <= 0:
                    particles.remove(particle)
                else:
                    particle.draw()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()