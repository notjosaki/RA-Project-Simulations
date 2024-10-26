import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np

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

        # Comprobar colisiones con las paredes del cubo
        for i in range(3):  # Para x, y, z
            if self.position[i] + self.radius > 1 or self.position[i] - self.radius < -1:
                self.velocity[i] = -self.velocity[i]  # Invertir dirección

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

def draw_cube():
    """Dibuja un cubo utilizando las aristas definidas."""
    glColor3f(1.0, 1.0, 1.0)  # Establecer el color de las aristas a blanco
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def setup_view(x_offset, y_offset, angle_x, angle_y):
    """Configura la vista en 3D."""
    glViewport(x_offset, y_offset, 400, 400)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 50.0)  # Perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)  # Posición de la cámara
    glRotatef(angle_x, 1, 0, 0)  # Rotar alrededor del eje X
    glRotatef(angle_y, 0, 1, 0)  # Rotar alrededor del eje Y

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Cubo 3D con Esferas en Movimiento y Explosiones')

    glClearColor(0.1, 0.1, 0.1, 1.0)  # Fondo oscuro
    glEnable(GL_DEPTH_TEST)  # Activar el test de profundidad

    spheres = []  # Lista para almacenar las esferas
    particles = []  # Lista para almacenar partículas

    clock = pygame.time.Clock()  # Para controlar el tiempo

    while True:
        delta_time = clock.tick(60) / 1000.0  # Tiempo desde el último frame en segundos

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_i:  # Si se presiona la tecla 'I' para esfera roja
                    # Generar una posición aleatoria dentro del cubo
                    x = random.uniform(-0.9, 0.9)
                    y = random.uniform(-0.9, 0.9)
                    z = random.uniform(-0.9, 0.9)
                    spheres.append(Sphere((x, y, z), color=(1.0, 0.0, 0.0)))  # Esfera roja
                elif event.key == K_o:  # Si se presiona la tecla 'O' para esfera azul
                    # Generar una posición aleatoria dentro del cubo
                    x = random.uniform(-0.9, 0.9)
                    y = random.uniform(-0.9, 0.9)
                    z = random.uniform(-0.9, 0.9)
                    spheres.append(Sphere((x, y, z), color=(0.0, 1.0, 1.0)))  # Esfera azul menos brillante

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
                    for _ in range(50):  # Generar 50 partículas
                        position = spheres[i].position.copy()  # Tomar la posición de la esfera
                        velocity = np.random.uniform(-0.1, 0.1, 3)  # Velocidades aleatorias
                        particles.append(Particle(position, velocity))

                    # Remover las esferas que chocan
                    del spheres[j]  # Primero eliminar la segunda esfera
                    del spheres[i]  # Luego eliminar la primera esfera
                    break  # Salir del bucle para evitar errores de índice
                j += 1
            else:
                i += 1  # Solo incrementa i si no se eliminó ninguna esfera

        # Actualizar partículas
        for particle in particles:
            particle.update(delta_time)

        # Filtrar partículas que han expirado
        particles = [p for p in particles if p.is_alive()]

        # Dibujar las diferentes vistas
        # Vista frontal
        setup_view(0, 400, 0, 0)
        draw_cube()
        for sphere in spheres:
            sphere.draw()
        
        # Dibujar partículas
        for particle in particles:
            glColor3f(0.5, 0.0, 0.5)  # Color de las partículas (lila)
            glPushMatrix()
            glTranslatef(*particle.position)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            glPopMatrix()

        # Vista lateral
        setup_view(400, 400, 0, 90)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        # Dibujar partículas
        for particle in particles:
            glColor3f(0.5, 0.0, 0.5)  # Color de las partículas (lila)
            glPushMatrix()
            glTranslatef(*particle.position)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            glPopMatrix()

        # Vista superior
        setup_view(0, 0, 90, 0)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        # Dibujar partículas
        for particle in particles:
            glColor3f(0.5, 0.0, 0.5)  # Color de las partículas (lila)
            glPushMatrix()
            glTranslatef(*particle.position)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            glPopMatrix()

        # Vista isométrica
        setup_view(400, 0, 30, 45)
        draw_cube()
        for sphere in spheres:
            sphere.draw()

        # Dibujar partículas
        for particle in particles:
            glColor3f(0.5, 0.0, 0.5)  # Color de las partículas (lila)
            glPushMatrix()
            glTranslatef(*particle.position)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            glPopMatrix()

        pygame.display.flip()  # Actualizar la pantalla
        pygame.time.wait(10)  # Esperar un poco para la próxima actualización

if __name__ == "__main__":
    main()




