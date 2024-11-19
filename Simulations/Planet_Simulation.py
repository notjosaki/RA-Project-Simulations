import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Astro:
    def __init__(self, massa, position=(0, 0, 0), radius=0.3):
        self.massa = massa  # En kilogramos (kg)
        self.position = np.array(position, dtype=float)  # Centro del astro
        self.radius = radius  # Radio visible del objeto

    def draw(self):
        """Dibujar el astro como una esfera."""
        glColor3f(1.0, 1.0, 0.0)  # Color amarillo para la esfera
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(*self.position)
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()

    def calculate_gravitational_influence(self, point, c=3e8):
        """Calcular la curvatura espacial en un punto dado."""
        G = 6.674e-11  # Constante gravitacional
        r = np.linalg.norm(np.array(point) - self.position)  # Distancia al centro del astro

        if r > self.radius:
            schwarzschild_radius = 2 * G * self.massa / c**2
            curvature_factor = schwarzschild_radius / r if r > 0 else 0
            return curvature_factor
        return 0  # Dentro del radio, la deformación será insignificante


def generate_points_inside_cube(spacing=0.4):
    """Generar puntos uniformemente distribuidos dentro del cubo."""
    points = []
    for x in np.arange(-1, 1, spacing):
        for y in np.arange(-1, 1, spacing):
            for z in np.arange(-1, 1, spacing):
                points.append((x, y, z))
    return points


def deform_point_towards_astro(point, astro, influence_factor=1.0):
    """Deformar un punto hacia un astro según su curvatura."""
    direction = astro.position - np.array(point)
    distance = np.linalg.norm(direction)
    curvature = astro.calculate_gravitational_influence(point)

    if distance > 0:
        deformation = curvature * influence_factor
        return np.array(point) + deformation * direction / distance
    return point


def draw_curved_lines(points, astro, max_distance=0.5, influence_factor=0.2):
    """Dibujar líneas deformadas hacia un astro."""
    glBegin(GL_LINES)
    for i, p1 in enumerate(points):
        for j, p2 in enumerate(points):
            if i < j:  # Evitar duplicar conexiones
                distance = np.linalg.norm(np.array(p1) - np.array(p2))
                if distance <= max_distance:
                    # Calcular el punto intermedio deformado
                    mid_point = (np.array(p1) + np.array(p2)) / 2
                    deformed_mid_point = deform_point_towards_astro(mid_point, astro, influence_factor)

                    # Calcular la distancia promedio de los puntos al astro
                    dist_to_astro_p1 = np.linalg.norm(np.array(p1) - astro.position)
                    dist_to_astro_p2 = np.linalg.norm(np.array(p2) - astro.position)
                    avg_distance_to_astro = (dist_to_astro_p1 + dist_to_astro_p2) / 2

                    # Normalizar el color basado en la distancia
                    max_influence = 2.0
                    influence = max(0, 1 - avg_distance_to_astro / max_influence)
                    glColor3f(1.0 * influence, 0.5 * influence, 1.0 - influence)

                    # Dibujar líneas curvadas con el punto deformado
                    glVertex3f(*p1)
                    glVertex3f(*deformed_mid_point)
                    glVertex3f(*deformed_mid_point)
                    glVertex3f(*p2)
    glEnd()


def setup_view(x_offset, y_offset, angle_x, angle_y, zoom):
    """Configurar la vista para una subventana."""
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
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Deformación del Espacio-Tiempo')

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    clock = pygame.time.Clock()
    zoom = 3.0  # Posición inicial de zoom

    # Crear un astro (por ejemplo, masa solar)
    astro = Astro(massa=1.989e30, radius=0.3)  # Masa del Sol

    # Generar puntos internos del cubo
    points = generate_points_inside_cube(spacing=0.4)

    # Velocidad del movimiento
    move_speed = 0.1

    while True:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda hacia arriba
                    zoom -= 0.1  # Acercar (zoom in)
                elif event.button == 5:  # Rueda hacia abajo
                    zoom += 0.1  # Alejar (zoom out)

        # Controlar el movimiento del astro con las teclas
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            astro.position[1] = min(1.0, astro.position[1] + move_speed)
        if keys[K_DOWN]:
            astro.position[1] = max(-1.0, astro.position[1] - move_speed)
        if keys[K_LEFT]:
            astro.position[0] = max(-1.0, astro.position[0] - move_speed)
        if keys[K_RIGHT]:
            astro.position[0] = min(1.0, astro.position[0] + move_speed)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Dibujar vistas
        for x_offset, y_offset, angle_x, angle_y in [(0, 300, 0, 0), (400, 300, 0, 90), (0, 0, 90, 0), (400, 0, 30, 45)]:
            setup_view(x_offset, y_offset, angle_x, angle_y, zoom)
            astro.draw()  # Dibujar el astro
            draw_curved_lines(points, astro, max_distance=0.5, influence_factor=0.0000099)

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    main()