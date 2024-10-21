import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
from Objects.sphere3 import Proton, Neutron, Electron, Photon  # Asegúrate de incluir todas las partículas

# --- Shader programs ---
vertex_shader = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    TexCoord = aTexCoord;
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

fragment_shader = """
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D texture1;

void main() {
    FragColor = texture(texture1, TexCoord);
}
"""

def create_sphere():
    latitudes = 30
    longitudes = 30
    radius = 0.5
    vertices = []
    tex_coords = []
    indices = []

    for i in range(latitudes + 1):
        theta = i * np.pi / latitudes
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        for j in range(longitudes + 1):
            phi = j * 2 * np.pi / longitudes
            sin_phi = np.sin(phi)
            cos_phi = np.cos(phi)

            x = cos_phi * sin_theta
            y = cos_theta
            z = sin_phi * sin_theta
            u = 1 - (j / longitudes)
            v = 1 - (i / latitudes)

            vertices.extend([x * radius, y * radius, z * radius])
            tex_coords.extend([u, v])

    for i in range(latitudes):
        for j in range(longitudes):
            first = i * (longitudes + 1) + j
            second = first + longitudes + 1
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])

    return np.array(vertices, dtype=np.float32), np.array(tex_coords, dtype=np.float32), np.array(indices, dtype=np.uint32)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('OpenGL Physics Simulation')

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Compilar shaders
    shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                            compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    glUseProgram(shader)

    # Crear geometría de la esfera
    vertices, tex_coords, indices = create_sphere()

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes + tex_coords.nbytes, None, GL_STATIC_DRAW)
    glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
    glBufferSubData(GL_ARRAY_BUFFER, vertices.nbytes, tex_coords.nbytes, tex_coords)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * np.dtype(np.float32).itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 2 * np.dtype(np.float32).itemsize, ctypes.c_void_p(vertices.nbytes))
    glEnableVertexAttribArray(1)

    # Crear las partículas (esferas)
    proton = Proton(position=[-2, 1, 0], velocity=[0.5, 0, 0])
    neutron = Neutron(position=[2, 1, 0], velocity=[-0.5, 0, 0])
    electron = Electron(position=[0, 0, 0], velocity=[0.1, 0.2, 0])
    photon = Photon(position=[-1, 0, 0], velocity=[0.3, 0, 0])

    # Configurar la cámara
    view = glm.lookAt(glm.vec3(0, 5, 10), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    projection = glm.perspective(glm.radians(45), 800 / 600, 0.1, 100)

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Actualizar posiciones de las partículas
        proton.update(dt)
        neutron.update(dt)
        electron.update(dt)
        photon.update(dt)

        # Comprobar colisiones
        if proton.check_swept_collision(neutron):
            proton.resolve_collision(neutron)

        # Dibujar las partículas
        for particle in [proton, neutron, electron, photon]:
            model = glm.translate(glm.mat4(1.0), glm.vec3(*particle.position))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
            glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
            glBindVertexArray(vao)
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
