import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm

# Configura shaders para el toroide
vertex_shader = """
#version 330
layout(location = 0) in vec3 in_position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main() {
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}
"""

fragment_shader = """
#version 330
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 1.0, 1.0, 1.0);  // Color blanco
}
"""

class Toroide:
    def __init__(self, context, radius=1.0, tube_radius=0.2, segments=50, rings=50, position=(0, 0, -5)):
        self.ctx = context
        self.radius = radius
        self.tube_radius = tube_radius
        self.segments = segments
        self.rings = rings
        self.position = glm.vec3(position)
        self.rotation_speed = 1.0  # Velocidad de rotación en grados
        self.rotation_enabled = False  # Bandera para activar/desactivar la rotación

        # Compilación de shaders
        self.shader = compileProgram(
            compileShader(vertex_shader, GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )
        glUseProgram(self.shader)

        # Creación de la malla del toroide
        self.vertices, self.indices = self.create_torus_mesh()
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Buffer de vértices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Buffer de índices
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # Matrices de transformación
        self.model_matrix = glm.mat4(1)
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(90.0), glm.vec3(0, 1, 0))  # Orientación en el eje X
        self.view_matrix = glm.translate(glm.mat4(1), self.position)
        self.projection_matrix = glm.perspective(glm.radians(45.0), 800/600, 0.1, 100.0)

        # Ubicación de matrices en el shader
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")
        self.projection_loc = glGetUniformLocation(self.shader, "projection")

        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, glm.value_ptr(self.view_matrix))
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, glm.value_ptr(self.projection_matrix))

    def create_torus_mesh(self):
        vertices = []
        indices = []

        for i in range(self.segments):
            theta = 2 * np.pi * i / self.segments
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            for j in range(self.rings):
                phi = 2 * np.pi * j / self.rings
                cos_phi = np.cos(phi)
                sin_phi = np.sin(phi)

                x = (self.radius + self.tube_radius * cos_phi) * cos_theta
                y = (self.radius + self.tube_radius * cos_phi) * sin_theta
                z = self.tube_radius * sin_phi
                vertices.extend([x, y, z])

                next_i = (i + 1) % self.segments
                next_j = (j + 1) % self.rings
                indices.extend([i * self.rings + j, i * self.rings + next_j])
                indices.extend([i * self.rings + j, next_i * self.rings + j])

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        return vertices, indices

    def update(self):
        # Solo rota el modelo si la bandera de rotación está habilitada
        if self.rotation_enabled:
            self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation_speed), glm.vec3(1, 0, 0))

    def draw(self):
        # Enviar matrices de transformación al shader
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, glm.value_ptr(self.model_matrix))
        
        # Renderizado en modo líneas
        glBindVertexArray(self.vao)
        glDrawElements(GL_LINES, len(self.indices), GL_UNSIGNED_INT, None)

    def toggle_rotation(self):
        self.rotation_enabled = not self.rotation_enabled  # Alterna el estado de rotación

    def cleanup(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo, self.ebo])
        glDeleteProgram(self.shader)

def main():
    # Inicialización de pygame y OpenGL
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Toroide en malla de alambre")
    clock = pygame.time.Clock()

    # Configuración de OpenGL
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Fondo negro

    # Crear instancia de la clase Toroide
    toroide = Toroide(context=None, radius=1.0, tube_radius=0.3, segments=60, rings=60, position=(0, 0, -5))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_g:
                    toroide.toggle_rotation()  # Alterna rotación al presionar 'G'

        # Limpiar pantalla
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Actualizar y dibujar el toroide
        toroide.update()
        toroide.draw()

        pygame.display.flip()
        clock.tick(60)

    # Limpieza
    toroide.cleanup()
    pygame.quit()

if __name__ == "__main__":
    main()
