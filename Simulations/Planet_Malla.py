import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from Menu_Planet import main_menu

class Astro:
    def __init__(self, massa, position=(0, 0), radius=0.5, color=(0.2, 0.6, 1.0), texture=None,name=None):
        self.massa = massa
        self.position = np.array(position, dtype=float)  # Posición en el plano
        self.radius = radius
        self.color = color
        self.texture = texture
        self.name=name
    def draw(self):
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.radius)

        if self.texture:  # Si hay textura, aplicarla
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            gluQuadricTexture(quadric, GL_TRUE)
            glColor3f(1.0, 1.0, 1.0)  # Color blanco para evitar mezcla de colores
        else:  # Si no hay textura, usar color sólido
            glColor3f(*self.color)

        gluSphere(quadric, self.radius, 32, 32)

        if self.texture:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()



def load_texture(image_path):
    """Cargar una textura desde un archivo."""
    texture_surface = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width, height = texture_surface.get_size()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture


def generate_grid(size=20, spacing=0.5):
    """Generar una malla de puntos para representar el espacio-tiempo."""
    grid = []
    for x in np.linspace(-size, size, int(2 * size / spacing)):
        for y in np.linspace(-size, size, int(2 * size / spacing)):
            grid.append([x, y, 0])
    return np.array(grid)


def deform_grid(grid, astros, G=6.674e-11, c=3e8):
    """Deformar la malla según la curvatura gravitacional de múltiples astros."""
    deformed_grid = grid.copy()
    for astro in astros:
        for i, point in enumerate(deformed_grid):
            x, y, z = point
            dx, dy = astro.position[0] - x, astro.position[1] - y
            distance = np.sqrt(dx**2 + dy**2)
            
            if distance > astro.position[0] - x: 
                schwarzschild_radius = 2 * G * astro.massa / c**2
                deformation = schwarzschild_radius / (distance + 1e-6)  # Gravedad decrece con la distancia
                
                # Aseguramos que la deformación siempre resta al eje Z
                z_new = z - deformation * 1000  # Escalar para visualización
                z = min(z, z_new)  # El nuevo Z nunca puede ser mayor que el actual

            elif distance > astro.position[1]-y: 
                schwarzschild_radius = 2 * G * astro.massa / c**2
                deformation = schwarzschild_radius / (distance + 1e-6)  # Gravedad decrece con la distancia
                
                # Aseguramos que la deformación siempre resta al eje Z
                z_new = z - deformation * 2000  # Escalar para visualización
                z = min(z, z_new)  # El nuevo Z nunca puede ser mayor que el actual            

            deformed_grid[i] = [x, y, z]
    return deformed_grid


def draw_grid(grid, color=(1, 1, 1)):
    """Dibujar la malla como una red de líneas."""
    glColor3f(*color)
    glBegin(GL_LINES)
    size = int(np.sqrt(len(grid)))
    for i in range(size):
        for j in range(size - 1):
            # Líneas en dirección X
            glVertex3f(*grid[i * size + j])
            glVertex3f(*grid[i * size + (j + 1)])
            # Líneas en dirección Y
            glVertex3f(*grid[j * size + i])
            glVertex3f(*grid[(j + 1) * size + i])
    glEnd()


def setup_camera(zoom):
    """Configurar la cámara para una vista 3D inclinada."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Configuración de la cámara con una vista inclinada y zoom
    gluLookAt(
        0, -30 + zoom, 30 + zoom,  # Posición de la cámara (x, y, z)
        0, 0, 0,                   # Hacia dónde mira la cámara (centro de la escena)
        0, 0, 1                    # Vector "arriba" (orientación)
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((700, 700), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Curvatura del Espacio-Tiempo (Vista 3D)')

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    # Cargar textura de Marte
    Textura = {
    "Earth": load_texture("Simulations/Imatges/earth.png"),
    "Mars": load_texture("Simulations/Imatges/marth.jpg"),
    "Jupiter": load_texture("Simulations/Imatges/jupiter.png"),
    "Venus": load_texture("Simulations/Imatges/venus.png"),
    "Saturn": load_texture("Simulations/Imatges/saturno.png"),
    "Mercury": load_texture("Simulations/Imatges/mercurio.png"),
    "Uranus": load_texture("Simulations/Imatges/urano.png"),
    "Neptune": load_texture("Simulations/Imatges/neptuno.png"),
    }

    planet_data = {
    "Mercury": {"massa": 3.3e23, "radius": 3},       # Radio proporcional más pequeño
    "Venus": {"massa": 4.87e24, "radius": 4.7},      # Aproximadamente proporcional a su tamaño real
    "Earth": {"massa": 5.97e24, "radius": 5},        # La Tierra se toma como referencia
    "Mars": {"massa": 6.42e23, "radius": 3.4},       # Marte es más pequeño que la Tierra
    "Jupiter": {"massa": 1.9e27, "radius": 15},      # Júpiter tiene el radio más grande (máximo de la escala)
    "Saturn": {"massa": 5.68e26, "radius": 12},      # Saturno es un poco más pequeño que Júpiter
    "Uranus": {"massa": 8.68e25, "radius": 8},       # Urano tiene un radio menor que Saturno
    "Neptune": {"massa": 1.02e26, "radius": 7.8},    # Neptuno es ligeramente más pequeño que Urano
    }


    a1=main_menu()
    a2=main_menu()

    p1=planet_data[a1.name]
    p2=planet_data[a2.name]
    t1=Textura[a1.name]
    t2=Textura[a2.name]
    astro1=Astro(p1['massa'],(-3,0),p1['radius'],(0,0,0),t1)
    astro2=Astro(p2['massa'],(3,0),p2['radius'],(0,0,0),t2)
    astro3 = Astro(5.97e24, (-3, 0), 1.0, (0.2, 0.6, 1.0),t1 )  # Astro 1
    astro4 = Astro(5.97e24, (3, 0), 1.0, (1.0, 0.6, 0.2),t2 )
    astros=[astro3,astro4]
    # Crear malla inicial
    grid = generate_grid(size=20, spacing=0.8)

    clock = pygame.time.Clock()
    zoom = 0
    min_zoom = -30
    max_zoom = 25

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda hacia arriba (zoom in)
                    zoom -= 1.0
                elif event.button == 5:  # Rueda hacia abajo (zoom out)
                    zoom += 1.0

        zoom = max(min_zoom, min(max_zoom, zoom))

        # Capturar las teclas presionadas
        keys = pygame.key.get_pressed()

        # Movimiento del astro 1 con teclas de flecha
        move_speed = 5.0  # Velocidad de movimiento
        if keys[K_UP]:
            astros[0].position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_DOWN]:
            astros[0].position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_LEFT]:
            astros[0].position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_RIGHT]:
            astros[0].position[0] += move_speed * clock.get_time() / 1000.0

        # Movimiento del astro 2 con teclas WASD
        if keys[K_w]:
            astros[1].position[1] += move_speed * clock.get_time() / 1000.0
        if keys[K_s]:
            astros[1].position[1] -= move_speed * clock.get_time() / 1000.0
        if keys[K_a]:
            astros[1].position[0] -= move_speed * clock.get_time() / 1000.0
        if keys[K_d]:
            astros[1].position[0] += move_speed * clock.get_time() / 1000.0

        # Deformar la malla según las posiciones de los astros
        deformed_grid = deform_grid(grid, astros)

        # Dibujar la escena
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_camera(zoom)
        draw_grid(deformed_grid)
        for astro in astros:
            astro.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

