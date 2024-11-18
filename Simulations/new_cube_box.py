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

# Función para cargar texturas
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
class Sphere:
    def __init__(self, position, texture_id, velocity=None, radius=0.05):
        self.position = np.array(position, dtype=float)
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius
        self.texture_id = texture_id

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

# Verificar colisiones entre partículas e interactuar
def check_collision_and_interact(sphere1, sphere2, spheres, textures):
    distance = np.linalg.norm(sphere1.position - sphere2.position)
    if distance < (sphere1.radius + sphere2.radius):
        # Interacciones específicas
        if sphere1.texture_id == textures['lepton'] and sphere2.texture_id == textures['boson']:
            # Lepton + Boson → Desintegración y partículas secundarias
            spheres.remove(sphere1)
            spheres.remove(sphere2)
            for _ in range(3):
                secondary_velocity = np.random.uniform(-0.01, 0.01, 3)
                spheres.append(Sphere(sphere1.position, textures['neutron'], velocity=secondary_velocity, radius=0.02))
        
        elif (sphere1.texture_id == textures['proton'] and sphere2.texture_id == textures['quark']) or \
             (sphere1.texture_id == textures['quark'] and sphere2.texture_id == textures['proton']):
            # Proton + Quark → Fusión en Higgs
            sphere1.texture_id = textures['higgs']
            spheres.remove(sphere2)
        
        elif sphere1.texture_id == textures['neutron'] or sphere2.texture_id == textures['neutron']:
            # Neutron → Repulsión
            sphere1.velocity = -sphere1.velocity
            sphere2.velocity = -sphere2.velocity

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
    pygame.display.set_caption('Simulación de Partículas con Texturas')

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Cargar texturas
    textures = {
        'lepton': load_texture(r'C:\Users\figue\Documents\UAB\UAB\Setè Quatri\Projecte RA\RA-Project-Simulations\Simulations\Imatges\textura-verde.png'),
        'neutron': load_texture(r'C:\Users\figue\Documents\UAB\UAB\Setè Quatri\Projecte RA\RA-Project-Simulations\Simulations\Imatges\textura-gris.png'),
        'proton': load_texture(r'C:\Users\figue\Documents\UAB\UAB\Setè Quatri\Projecte RA\RA-Project-Simulations\Simulations\Imatges\textura-azul.png'),
        'quark': load_texture(r'C:\Users\figue\Documents\UAB\UAB\Setè Quatri\Projecte RA\RA-Project-Simulations\Simulations\Imatges\textura-morada.png'),
        'boson': load_texture(r'C:\Users\figue\Documents\UAB\UAB\Setè Quatri\Projecte RA\RA-Project-Simulations\Simulations\Imatges\textura-roja.png'),
        'higgs': load_texture(r'C:\Users\figue\Documents\UAB\UAB\Setè Quatri\Projecte RA\RA-Project-Simulations\Simulations\Imatges\textura-amarilla.png'),
    }

    spheres = []
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
                x, y, z = random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9)
                if event.key == K_l:
                    spheres.append(Sphere((x, y, z), texture_id=textures['lepton']))
                elif event.key == K_n:
                    spheres.append(Sphere((x, y, z), texture_id=textures['neutron']))
                elif event.key == K_p:
                    spheres.append(Sphere((x, y, z), texture_id=textures['proton']))
                elif event.key == K_q:
                    spheres.append(Sphere((x, y, z), texture_id=textures['quark']))
                elif event.key == K_b:
                    spheres.append(Sphere((x, y, z), texture_id=textures['boson']))
                elif event.key == K_h:
                    spheres.append(Sphere((x, y, z), texture_id=textures['higgs']))
                elif event.key == K_k:
                    speed_factor = 0.3
            if event.type == KEYUP:
                if event.key == K_k:
                    speed_factor = 1.0
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom -= 0.1
                elif event.button == 5:
                    zoom += 0.1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for x_offset, y_offset, angle_x, angle_y in [(0, 400, 0, 0), (400, 400, 0, 90), (0, 0, 90, 0), (400, 0, 30, 45)]:
            setup_view(x_offset, y_offset, angle_x, angle_y, zoom)
            draw_cube()

            for sphere in spheres[:]:
                sphere.update(speed_factor)
                sphere.draw()

            for i in range(len(spheres) - 1):
                for j in range(i + 1, len(spheres)):
                    if i < len(spheres) and j < len(spheres):
                        check_collision_and_interact(spheres[i], spheres[j], spheres, textures)

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

