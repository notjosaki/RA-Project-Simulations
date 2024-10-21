import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
from Objects.sphere3 import Sphere
from Objects.wall import Wall
from Objects.cube import Cube
from PIL import Image

# --- Shader programs ---
vertex_shader_sphere = """
#version 330 core
layout(location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

fragment_shader_sphere = """
#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(1.0, 1.0, 1.0, 1.0); // Color blanco
}
"""

# --- Shader programs ---
vertex_shader_cube = """
#version 330 core
layout(location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

fragment_shader_cube = """
#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Color rojo
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

def create_cube():
    vertices = [
        # Cara frontal
        -0.5, -0.5,  0.5,
         0.5, -0.5,  0.5,
         0.5,  0.5,  0.5,
        -0.5,  0.5,  0.5,

        # Cara trasera
        -0.5, -0.5, -0.5,
         0.5, -0.5, -0.5,
         0.5,  0.5, -0.5,
        -0.5,  0.5, -0.5,
    ]

    indices = [
        # Cara frontal
        0, 1, 2,
        2, 3, 0,

        # Cara trasera
        4, 5, 6,
        6, 7, 4,

        # Cara izquierda
        0, 3, 7,
        7, 4, 0,

        # Cara derecha
        1, 2, 6,
        6, 5, 1,

        # Cara superior
        3, 2, 6,
        6, 7, 3,

        # Cara inferior
        0, 1, 5,
        5, 4, 0
    ]

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def load_texture(path):
    image = Image.open(path)
    img_data = image.convert("RGBA").tobytes()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture

def main_sphere():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('OpenGL Physics Simulation')

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    shader = compileProgram(compileShader(vertex_shader_sphere, GL_VERTEX_SHADER),
                            compileShader(fragment_shader_sphere, GL_FRAGMENT_SHADER))
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

def main_cube():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('OpenGL Cube Physics Simulation')

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    shader = compileProgram(compileShader(vertex_shader_cube, GL_VERTEX_SHADER),
                            compileShader(fragment_shader_cube, GL_FRAGMENT_SHADER))
    glUseProgram(shader)

    vertices, indices = create_cube()
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)  # Element buffer object

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * np.dtype(np.float32).itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Inicializar cubos
    cube1 = Cube(position=[-3.0, 5.0, 0.0], velocity=[1.0, 0.0, 0.0], size=1.0)
    cube2 = Cube(position=[3.0, 5.0, 0.0], velocity=[-1.0, 0.0, 0.0], size=1.0)
    cubes = [cube1, cube2]

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

        # Actualizar y dibujar cubos
        for cube in cubes:
            cube.update(dt)

            model = glm.translate(glm.mat4(1.0), glm.vec3(*cube.position))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
            glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

            glBindVertexArray(vao)
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

        pygame.display.flip()

    pygame.quit()


question_option = str(input("\nVols realitzar una simulació de particules amb: \n1. Esferes\n2. Cubs\n\n--> "))
while question_option not in ["1", "2"]:
    question_option = str(input("\nTorna a introduïr el valor: \n1. Esferes\n2. Cubs\n\n-->  "))

if question_option == "1":
    if __name__ == "__main__":
        main_sphere()
else:
    if __name__ == "__main__":
        main_cube()

