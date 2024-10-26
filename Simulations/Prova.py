import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import glm

# Define los planetas
class Planet:
    def __init__(self, position, velocity, radius, texture):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.radius = radius
        self.texture = texture
        self.rotation_angle = 0

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation_angle, 0, 1, 0)
        gluSphere(gluNewQuadric(), self.radius, 32, 32)
        glPopMatrix()
        self.rotation_angle += 1  # Rotate for better visualization

    def update(self):
        self.position += self.velocity


def load_texture(image_path):
    texture_surface = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
    width, height = texture_surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    return texture_id


def draw_background():
    glBegin(GL_QUADS)
    glColor3f(0, 0, 0)  # Space color
    glVertex3f(-1000, -1000, -1000)
    glVertex3f(1000, -1000, -1000)
    glVertex3f(1000, 1000, -1000)
    glVertex3f(-1000, 1000, -1000)
    glEnd()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 1000)
    glTranslatef(0.0, 0.0, -10)
    glEnable(GL_TEXTURE_2D)

    # Cargar texturas de planetas
    earth_texture = load_texture('earth_texture.jpg')  # Asegúrate de tener una textura de la Tierra
    mars_texture = load_texture('mars_texture.jpg')    # Asegúrate de tener una textura de Marte

    # Crear planetas
    earth = Planet(position=[2, 0, 0], velocity=[0, 0, 0], radius=1, texture=earth_texture)
    mars = Planet(position=[-2, 0, 0], velocity=[0.01, 0, 0], radius=0.5, texture=mars_texture)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_background()

        # Actualizar y dibujar planetas
        earth.update()
        mars.update()
        earth.draw()
        mars.draw()

        # Colisión simplificada (puedes hacerla más compleja)
        if np.linalg.norm(earth.position - mars.position) < (earth.radius + mars.radius):
            print("Colisión detectada!")
            # Aquí puedes añadir una explosión o cualquier efecto deseado

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    main()
