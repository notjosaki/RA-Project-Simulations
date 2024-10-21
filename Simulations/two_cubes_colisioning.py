import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
import time

# Definición del cubo
class Cube:
    def __init__(self, position, velocity, size, mass=1.0):
        self.position = np.array(position, dtype=np.float64)
        self.previous_position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.size = size
        self.half_size = size / 2
        self.mass = mass

    def update(self, dt):
        self.previous_position = np.copy(self.position)
        self.position += self.velocity * dt
        self.velocity[1] -= 9.81 * dt  # Gravedad

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.half_size < 0:
            self.position[1] = self.half_size
            self.velocity[1] = -self.velocity[1] * 0.9  # Rebote

    def check_swept_collision(self, other):
        displacement_self = glm.dvec3(*self.position) - glm.dvec3(*self.previous_position)
        displacement_other = glm.dvec3(*other.position) - glm.dvec3(*other.previous_position)
        relative_displacement = displacement_self - displacement_other
        initial_vector = glm.dvec3(*self.previous_position) - glm.dvec3(*other.previous_position)
        distance_at_closest_approach = glm.dot(initial_vector, glm.normalize(relative_displacement))
        if distance_at_closest_approach < self.half_size + other.half_size:
            return True
        return False

    def resolve_collision(self, other):
        collision_vector = glm.dvec3(*self.position) - glm.dvec3(*other.position)
        distance = glm.length(collision_vector)
        min_distance = self.half_size + other.half_size
        if distance < min_distance:
            collision_normal = glm.normalize(collision_vector)
            overlap = min_distance - distance
            self.position += collision_normal * overlap * 0.5
            other.position -= collision_normal * overlap * 0.5
            relative_velocity = self.velocity - other.velocity
            velocity_along_normal = glm.dot(glm.dvec3(*relative_velocity), collision_normal)
            if velocity_along_normal > 0:
                return
            restitution = 0.8
            impulse_magnitude = -(1 + restitution) * velocity_along_normal
            impulse_magnitude /= (1 / self.mass + 1 / other.mass)
            impulse = collision_normal * impulse_magnitude
            self.velocity += impulse / self.mass
            other.velocity -= impulse / other.mass


# Vertices del cubo para OpenGL
vertices = [
    -0.5, -0.5, -0.5,
     0.5, -0.5, -0.5,
     0.5,  0.5, -0.5,
    -0.5,  0.5, -0.5,
    -0.5, -0.5,  0.5,
     0.5, -0.5,  0.5,
     0.5,  0.5,  0.5,
    -0.5,  0.5,  0.5
]

indices = [
    0, 1, 2, 2, 3, 0,  # Back face
    4, 5, 6, 6, 7, 4,  # Front face
    0, 1, 5, 5, 4, 0,  # Bottom face
    3, 2, 6, 6, 7, 3,  # Top face
    0, 3, 7, 7, 4, 0,  # Left face
    1, 2, 6, 6, 5, 1   # Right face
]

# Shader de vértices y fragmentos
vertex_shader_src = """
#version 330
layout(location = 0) in vec3 position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

fragment_shader_src = """
#version 330
out vec4 outColor;
void main() {
    outColor = vec4(1.0, 0.5, 0.2, 1.0);  // Color del cubo
}
"""

# Inicialización de GLFW y OpenGL
def create_window():
    if not glfw.init():
        return None
    window = glfw.create_window(800, 600, "Cube Simulation", None, None)
    if not window:
        glfw.terminate()
        return None
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    return window

# Compilar shaders
def compile_shader_program():
    program = compileProgram(
        compileShader(vertex_shader_src, GL_VERTEX_SHADER),
        compileShader(fragment_shader_src, GL_FRAGMENT_SHADER)
    )
    return program

# Matrices de cámara y proyección
def create_projection_matrix():
    return glm.perspective(glm.radians(45), 800/600, 0.1, 100.0)

def create_view_matrix():
    return glm.lookAt(glm.vec3(0, 10, 20), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

# Dibujar un cubo
def draw_cube(shader_program, cube):
    model = glm.translate(glm.mat4(1.0), glm.vec3(*cube.position))
    model = glm.scale(model, glm.vec3(cube.size))
    
    model_loc = glGetUniformLocation(shader_program, "model")
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
    
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

# Simulación y renderizado
def simulate_and_render():
    window = create_window()
    if not window:
        return

    shader_program = compile_shader_program()
    glUseProgram(shader_program)

    projection = create_projection_matrix()
    view = create_view_matrix()
    projection_loc = glGetUniformLocation(shader_program, "projection")
    view_loc = glGetUniformLocation(shader_program, "view")
    
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection))
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

    # Buffers de vértices e índices
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW)

    # Atributos de vértices
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # Configurar cubos
    cube1 = Cube(position=[-1, 1, 0], velocity=[2, 0, 0], size=1, mass=1.0)
    cube2 = Cube(position=[2, 1, 0], velocity=[-1, 0, 0], size=1, mass=1.0)
    
    dt = 0.016  # Tiempo de paso (aproximadamente 60 FPS)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Actualizar simulación de física
        cube1.update(dt)
        cube2.update(dt)

        if cube1.check_swept_collision(cube2):
            cube1.resolve_collision(cube2)

        # Dibujar cubos
        draw_cube(shader_program, cube1)
        draw_cube(shader_program, cube2)

        glfw.swap_buffers(window)
        glfw.poll_events()
        time.sleep(dt)

    glfw.terminate()

if __name__ == "__main__":
    simulate_and_render()
