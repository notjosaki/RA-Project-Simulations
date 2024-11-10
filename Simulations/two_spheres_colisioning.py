import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import random
from OpenGL.GLU import *
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

# Compilar shaders
def compile_shader_program():
    vertex_shader_src = """
    #version 330 core
    layout(location = 0) in vec3 position;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    void main() {
        gl_Position = projection * view * model * vec4(position, 1.0);
    }
    """

    fragment_shader_src = """
    #version 330 core
    out vec4 outColor;
    void main() {
        outColor = vec4(0.2, 0.5, 1.0, 1.0);  // Color de la esfera
    }
    """

    program = compileProgram(
        compileShader(vertex_shader_src, GL_VERTEX_SHADER),
        compileShader(fragment_shader_src, GL_FRAGMENT_SHADER)
    )
    return program

# Clase para representar esferas
class Sphere:
    def __init__(self, position, color, velocity=None, radius=0.05):
        self.position = np.array(position, dtype=float)
        self.color = color
        self.velocity = velocity if velocity is not None else np.random.uniform(-0.02, 0.02, 3)
        self.radius = radius
        self.shader_program = compile_shader_program()  # Compilar el shader
        self.vertices = self.generate_sphere_vertices()

    def generate_sphere_vertices(self, slices=10, stacks=10):
        """Genera los vértices de una esfera."""
        vertices = []
        for i in range(stacks + 1):
            lat = np.pi * i / stacks
            for j in range(slices + 1):
                lon = 2 * np.pi * j / slices
                x = self.radius * np.sin(lat) * np.cos(lon)
                y = self.radius * np.sin(lat) * np.sin(lon)
                z = self.radius * np.cos(lat)
                vertices.append((x, y, z))
        return np.array(vertices, dtype='float32')

    def draw(self):
        """Dibuja la esfera utilizando shaders."""
        glUseProgram(self.shader_program)  # Activar el programa de shader

        # Matrices de transformación
        model = np.identity(4)
        model = self.translate_matrix(self.position)

        view = np.identity(4)
        projection = np.identity(4)
        gluPerspective(45, 1, 0.1, 50.0)

        # Pasar las matrices al shader
        model_loc = glGetUniformLocation(self.shader_program, "model")
        view_loc = glGetUniformLocation(self.shader_program, "view")
        projection_loc = glGetUniformLocation(self.shader_program, "projection")

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)

        # Dibujar la esfera
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.vertices))
        glDisableClientState(GL_VERTEX_ARRAY)

    def translate_matrix(self, position):
        """Crea una matriz de translación."""
        matrix = np.identity(4)
        matrix[3, :3] = position  # La última fila se utiliza para la traslación
        return matrix

    def update(self):
        """Actualiza la posición de la esfera y maneja colisiones."""
        # Actualizar la posición
        self.position += self.velocity

        # Comprobar colisiones con las paredes del cubo
        for i in range(3):  # Para x, y, z
            if self.position[i] + self.radius > 1 or self.position[i] - self.radius < -1:
                self.velocity[i] = -self.velocity[i]  # Invertir dirección

    def check_collision(self, other):
        """Comprueba si hay colisión con otra esfera."""
        distance = np.linalg.norm(self.position - other.position)
        if distance < self.radius + other.radius:
            # Calcular la normal y la dirección del rebote
            normal = (self.position - other.position) / distance
            relative_velocity = self.velocity - other.velocity
            velocity_along_normal = np.dot(relative_velocity, normal)

            if velocity_along_normal > 0:
                return  # Las esferas se están separando

            # Calcula la restitución
            restitution = 1.0  # Coeficiente de restitución
            j = -(1 + restitution) * velocity_along_normal
            j /= 2  # Para el caso de colisiones entre dos esferas

            # Aplicar el impulso a las esferas
            self.velocity += j * normal
            other.velocity -= j * normal

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
    pygame.display.set_caption('Cubo 3D con Esferas en Movimiento')

    glClearColor(0.1, 0.1, 0.1, 1.0)  # Fondo oscuro
    glEnable(GL_DEPTH_TEST)  # Activar el test de profundidad

    spheres = []  # Lista para almacenar las esferas

    while True:
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
                    spheres.append(Sphere((x, y, z), color=(0.0, 0.0, 0.5)))  # Esfera azul menos brillante

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Actualizar y dibujar las esferas
        for sphere in spheres:
            sphere.update()

        # Comprobar colisiones entre esferas
        for i in range(len(spheres)):
            for j in range(i + 1, len(spheres)):
                spheres[i].check_collision(spheres[j])

        # Dibujar las diferentes vistas
        for i in range(4):
            setup_view(i % 2 * 400, (i // 2) * 400, 0, 90 * (i % 2))
            draw_cube()
            for sphere in spheres:
                sphere.draw()  # Dibujar las esferas

        pygame.display.flip()  # Actualizar la pantalla
        pygame.time.wait(10)  # Esperar un poco para la próxima actualización

if __name__ == "__main__":
    main()

