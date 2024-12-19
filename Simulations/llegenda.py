import pygame 
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np   

class Astro:
    def __init__(self, massa, position=(0, 0), radius=0.5, color=(0.2, 0.6, 1.0), texture=None, name="", has_rings=False):
        self.massa = massa
        self.position = np.array(position, dtype=float)  # Posición en el plano
        self.radius = radius
        self.color = color
        self.texture = texture
        self.name = name
        self.has_rings = has_rings  # Indica si tiene anillos
        self.is_hovered = False  # Indica si el ratón está sobre el planeta

    def draw(self, rotation_angle=0):
        """Dibujar el planeta, opcionalmente con rotación."""
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.radius)
        glRotatef(rotation_angle, 0, 1, 0)  # Rotación sobre el eje Y (como la Tierra)

        # Cambiar el radio si está seleccionado
        current_radius = self.radius * (1.2 if self.is_hovered else 1.0)

        if self.texture:  # Si hay textura, aplicarla
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            gluQuadricTexture(quadric, GL_TRUE)
            glColor3f(1.0, 1.0, 1.0)  # Color blanco para evitar mezcla de colores
        else:  # Si no hay textura, usar color sólido
            glColor3f(*self.color)

        gluSphere(quadric, current_radius, 32, 32)

        if self.texture:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()

        # Dibujar los anillos si los tiene
        if self.has_rings:
            self.draw_rings()

    def draw_rings(self):
        """Dibujar los anillos del planeta."""
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.radius)  # Mover al centro del planeta
        glColor4f(0.8, 0.8, 0.8, 0.6)  # Color gris claro con transparencia

        # Dibujar los anillos con GL_TRIANGLE_STRIP
        num_segments = 100
        inner_radius = self.radius * 1.5
        outer_radius = self.radius * 2.5
        glBegin(GL_TRIANGLE_STRIP)
        for i in range(num_segments + 1):
            angle = 2 * np.pi * i / num_segments
            x = np.cos(angle)
            y = np.sin(angle)
            glVertex3f(inner_radius * x, inner_radius * y, 0)
            glVertex3f(outer_radius * x, outer_radius * y, 0)
        glEnd()

        glPopMatrix()

    def draw_name(self):
        """Dibujar el nombre del planeta justo debajo de su posición."""
        x_offset = self.position[0] * 40 + 400  # Ajusta la posición horizontal del nombre
        y_offset = -self.position[1] * 40 + 400 - (self.radius * 40 + 20)  # Ajusta la posición vertical del nombre (debajo del planeta)
        draw_text(self.name, (x_offset, y_offset), size=16)

    def check_collision(self, mouse_x, mouse_y):
        """Comprobar si el puntero del ratón está sobre el planeta."""
        world_mouse_x = (mouse_x / 800) * 20 - 10  # Convertir de coordenadas de pantalla a coordenadas del mundo
        world_mouse_y = ((mouse_y / 800) * -20) + 10  # Corregir la Y para que coincida con el sistema de coordenadas de OpenGL
        distance = np.sqrt((world_mouse_x - self.position[0])**2 + (world_mouse_y - self.position[1])**2)
        self.is_hovered = distance <= self.radius



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


def setup_camera(zoom):
    """Configurar la cámara para una vista 3D inclinada."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -30 + zoom, 30 + zoom, 0, 0, 0, 0, 0, 1)


def setup_camera_menu():
    """Configurar la cámara para el menú inicial."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 30, 0, 0, 0, 0, 1, 0)


def main_menu(planets):
    """Pantalla del menú principal con planetas giratorios."""
    rotation_angle = 0
    clock = pygame.time.Clock()
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        selected_planet = None

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                return None
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        for planet in planets:
            planet.check_collision(*mouse_pos)
            if planet.is_hovered and mouse_clicked:
                selected_planet = planet
                print(f"Planeta '{planet.name}' seleccionado.")
                return selected_planet

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_camera_menu()

        for planet in planets:
            planet.draw(rotation_angle)
            planet.draw_name()

        draw_text("Selecciona qualsevol Particula", (150, 100), size=20, color=(255, 255, 255))
        draw_text("ESC per sortir", (280, 60), size=15, color=(200, 200, 200))

        pygame.display.flip()
        rotation_angle += 1
        clock.tick(60)

def draw_text(text, position, size=20, color=(255, 255, 255)):
    """Dibujar texto en la pantalla."""
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color, (0, 0, 0, 0))  # Transparente de fondo
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)



def main():
    pygame.init()
    pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Planetas Giratorios")

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Cargar texturas
    texture_earth = load_texture("Simulations/Imatges/proton.png")
    texture_mars = load_texture("Simulations/Imatges/neutron.png")
    texture_jupiter = load_texture("Simulations/Imatges/boson.png")
    texture_venus = load_texture("Simulations/Imatges/lepton.png")
    texture_higghs = load_texture("Simulations/Imatges/higgs.png")
    texture_quark = load_texture("Simulations/Imatges/quark.png")

    # Crear planetas
    planets = [
    Astro(1, (-6, -3), 1.5, texture=texture_earth, name="Proton"),  # Arriba a la izquierda
    Astro(1, (0, -4), 1.5, texture=texture_mars, name="Neutron"),    # Directamente arriba
    Astro(1, (6, -3), 1.5, texture=texture_jupiter, name="Boson"),   # Arriba a la derecha
    Astro(1, (-6, 3), 1.5, texture=texture_venus, name="Lepton"),  # Abajo a la izquierda
    Astro(1, (0, 4), 1.5, texture=texture_higghs, name="B-Higghs"), # Directamente abajo
    Astro(1, (6, 3), 1.5, texture=texture_quark, name="Quarks")    # Abajo a la derecha
    ]       


    main_menu(planets)

if __name__ == "__main__":
    main()