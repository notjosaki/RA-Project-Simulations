import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np

# Definir los vértices y las aristas del tubo
def draw_cylinder(radius=1, height=4, slices=30):
    glBegin(GL_QUADS)
    for i in range(slices):
        theta1 = (i / slices) * 2 * np.pi
        theta2 = ((i + 1) / slices) * 2 * np.pi
        x1 = radius * np.cos(theta1)
        y1 = radius * np.sin(theta1)
        x2 = radius * np.cos(theta2)
        y2 = radius * np.sin(theta2)

        # Puntos de la base inferior
        glVertex3f(x1, y1, -height / 2)
        glVertex3f(x2, y2, -height / 2)
        glVertex3f(x2, y2, height / 2)
        glVertex3f(x1, y1, height / 2)
    glEnd()

# Clase para representar partículas
class Particle:
    def __init__(self, position, velocity):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.lifetime = 1.0  # Vida de la partícula en segundos

    def update(self, delta_time):
        """Actualiza la posición y la vida de la partícula."""
        self.position += self.velocity * delta_time
        self.lifetime -= delta_time

    def is_alive(self):
        """Comprueba si la partícula sigue viva."""
        return self.lifetime > 0

# Clase para representar esferas
class Sphere:
    def __init__(self, position, color, velocity=None, radius=0.05):
        self.position = np.array(position, dtype=float)
        self.color = color  # Color de la esfera
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius

    def update(self):
        """Actualiza la posición de la esfera y maneja colisiones."""
        # Actualizar la posición
        self.position += self.velocity

        # Comprobar colisiones con las paredes del tubo (cylinder)
        for i in range(2):  # Para arriba y abajo
            if self.position[i] + self.radius > 2 or self.position[i] - self.radius < -2:
                self.velocity[i] = -self.velocity[i]  # Invertir dirección
        
        # Comprobar colisiones con el cilindro
        distance_from_center = np.linalg.norm(self.position[:2])
        if distance_from_center + self.radius > 1:  # Radii del cilindro
            normal = self.position[:2] / distance_from_center  # Normal unitario
            self.velocity[:2] = -self.velocity[:2] * normal  # Rebotar en la pared

    def draw(self):
        """Dibuja la esfera en su posición."""
        slices = 10
        stacks = 10
        glPushMatrix()
        glTranslatef(*self.position)  # Mover la esfera a su posición
        glColor3f(*self.color)  # Establecer el color de la esfera
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, self.radius, slices, stacks)
        glPopMatrix()

    def check_collision(self, other):
        """Comprueba si hay colisión con otra esfera."""
        distance = np.linalg.norm(self.position - other.position)
        if distance < self.radius + other.radius:
            # Colisión detectada, comprobar si son de diferentes colores
            if self.color != other.color:
                # Generar explosión de partículas
                return True  # Indica que hay una colisión con explosión
            # Calcular la dirección de la colisión
            normal = (self.position - other.position) / distance  # Normal unitario
            relative_velocity = self.velocity - other.velocity
            
            # Velocidades en la dirección normal
            velocity_along_normal = np.dot(relative_velocity, normal)
            
            # Si las esferas se acercan
            if velocity_along_normal < 0:
                # Coeficiente de restitución (elasticidad)
                restitution = 1.0
                
                # Calcular impulso escalar
                impulse_magnitude = -(1 + restitution) * velocity_along_normal
                impulse = impulse_magnitude * normal
                
                # Aplicar el impulso
                self.velocity += impulse
                other.velocity -= impulse

        return False  # No hubo colisión que genere explosión

def setup_view(camera_position):
    """Configura la vista en 3D."""
    glViewport(0, 0, 800, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)  # Perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Definir el punto al que mira la cámara y el vector arriba
    look_at = (0, 0, 0)
    up_vector = (0, 1, 0)

    gluLookAt(*camera_position, *look_at, *up_vector)  # Usar la posición de la cámara pasada

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Cilindro 3D con Esferas en Movimiento y Explosiones')

    glClearColor(0.1, 0.1, 0.1, 1.0)  # Fondo oscuro
    glEnable(GL_DEPTH_TEST)  # Activar el test de profundidad

    spheres = []  # Lista para almacenar las esferas
    particles = []  # Lista para almacenar partículas

    clock = pygame.time.Clock()  # Para controlar el tiempo

    # Posiciones de las cámaras
    camera_positions = [
        (0, 5, 5),   # Vista desde el lado
        (0, 0, 5),   # Vista desde el agujero de arriba
        (0, 0, -5)   # Vista desde el agujero de abajo
    ]
    current_camera = 0  # Inicialmente la cámara desde el lado

    setup_view(camera_positions[current_camera])  # Configurar la vista

    while True:
        delta_time = clock.tick(60) / 1000.0  # Tiempo desde el último frame en segundos

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_i:  # Si se presiona la tecla 'I' para esfera roja
                    # Generar una posición aleatoria dentro del tubo
                    x = random.uniform(-0.5, 0.5)
                    y = random.uniform(-0.5, 0.5)
                    z = random.uniform(-2, 2)  # Altura dentro del tubo
                    spheres.append(Sphere((x, y, z), color=(1.0, 0.0, 0.0)))  # Esfera roja
                elif event.key == K_o:  # Si se presiona la tecla 'O' para esfera azul
                    # Generar una posición aleatoria dentro del tubo
                    x = random.uniform(-0.5, 0.5)
                    y = random.uniform(-0.5, 0.5)
                    z = random.uniform(-2, 2)  # Altura dentro del tubo
                    spheres.append(Sphere((x, y, z), color=(0.0, 1.0, 1.0)))  # Esfera azul
                elif event.key == K_SPACE:  # Cambiar la vista de la cámara
                    current_camera = (current_camera + 1) % len(camera_positions)  # Cambiar a la siguiente cámara
                    setup_view(camera_positions[current_camera])  # Actualizar la vista

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Actualizar y dibujar las esferas
        for sphere in spheres:
            sphere.update()

        # Comprobar colisiones entre esferas y generar partículas si es necesario
        i = 0
        while i < len(spheres):
            j = i + 1
            while j < len(spheres):
                if spheres[i].check_collision(spheres[j]):
                    # Generar explosión de partículas
                    for _ in range(10):
                        particle = Particle(spheres[i].position.copy(), np.random.uniform(-0.01, 0.01, 3))
                        particles.append(particle)
                j += 1
            i += 1

        # Actualizar y dibujar partículas
        for particle in particles:
            particle.update(delta_time)
            if not particle.is_alive():
                particles.remove(particle)
            else:
                glPushMatrix()
                glTranslatef(*particle.position)
                glColor3f(1.0, 1.0, 0.0)  # Color amarillo para las partículas
                gluSphere(gluNewQuadric(), 0.02, 10, 10)  # Dibujar las partículas
                glPopMatrix()

        # Dibujar el cilindro
        draw_cylinder(radius=1, height=4, slices=30)

        # Dibujar las esferas
        for sphere in spheres:
            sphere.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()
