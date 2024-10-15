import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
from Objects.sphere import Sphere
from Objects.wall import Wall

# --- Shader programs ---
vertex_shader = """
#version 330 core
layout(location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

fragment_shader = """
#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(1.0, 1.0, 1.0, 1.0); // Color blanco
}
"""

def create_sphere():
    latitudes = 30
    longitudes = 30
    radius = 0.5
    vertices = []

    for i in range(latitudes + 1):
        theta = i * np.pi / latitudes
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        for j in range(longitudes + 1):
            phi = j * 2 * np.pi / longitudes
            sin_phi = np.sin(phi)
            cos_phi = np.cos(phi)

            x = cos_phi * sin_theta * radius
            y = cos_theta * radius
            z = sin_phi * sin_theta * radius
            vertices.extend([x, y, z])

    return np.array(vertices, dtype=np.float32)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('OpenGL Physics Simulation')

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                            compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    glUseProgram(shader)

    vertices = create_sphere()
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * np.dtype(np.float32).itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Inicializar esferas
    sphere1 = Sphere(position=[-3.0, 5.0, 0.0], velocity=[1.0, 0.0, 0.0], radius=0.5)
    sphere2 = Sphere(position=[3.0, 5.0, 0.0], velocity=[-1.0, 0.0, 0.0], radius=0.5)
    spheres = [sphere1, sphere2]

    # Crear muros
    walls = [Wall(position=[-4.5, -1, 0], width=1, height=2),  # Muro izquierdo
             Wall(position=[4.5, -1, 0], width=1, height=2)]  # Muro derecho

    # Configurar la cámara
    view = glm.lookAt(glm.vec3(0, 10, 20), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    projection = glm.perspective(glm.radians(45), 800 / 600, 0.1, 100)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Actualizar y dibujar esferas
        for sphere in spheres:
            sphere.update(dt)

            # Colisiones entre esferas
            for other in spheres:
                if sphere != other and sphere.check_collision(other):
                    sphere.resolve_collision(other)

            # Colisiones con muros
            for wall in walls:
                if wall.check_collision(sphere):
                    wall.resolve_collision(sphere)

            model = glm.translate(glm.mat4(1.0), glm.vec3(*sphere.position))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
            glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, len(vertices) // 3)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
