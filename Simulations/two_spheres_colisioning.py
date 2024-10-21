import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
import time

# Definición de la esfera
class Sphere:
    def __init__(self, position, velocity, radius, mass=1.0):
        self.position = np.array(position, dtype=np.float64)
        self.previous_position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.mass = mass

    def update(self, dt):
        self.previous_position = np.copy(self.position)
        self.position += self.velocity * dt
        self.velocity[1] -= 9.81 * dt  # Gravedad

        # Rebote en el suelo (plano y=0)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Rebote

    def check_swept_collision(self, other):
        displacement_self = glm.dvec3(*self.position) - glm.dvec3(*self.previous_position)
        displacement_other = glm.dvec3(*other.position) - glm.dvec3(*other.previous_position)
        relative_displacement = displacement_self - displacement_other
        initial_vector = glm.dvec3(*self.previous_position) - glm.dvec3(*other.previous_position)
        distance_at_closest_approach = glm.dot(initial_vector, glm.normalize(relative_displacement))
        if distance_at_closest_approach < self.radius + other.radius:
            return True
        return False

    def resolve_collision(self, other):
        collision_vector = glm.dvec3(*self.position) - glm.dvec3(*other.position)
        distance = glm.length(collision_vector)
        min_distance = self.radius + other.radius
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


# Inicialización de GLFW y OpenGL
def create_window():
    if not glfw.init():
        return None
    window = glfw.create_window(800, 600, "Sphere Simulation", None, None)
    if not window:
        glfw.terminate()
        return None
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    return window

# Compilar shaders
def compile_shader_program():
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
        outColor = vec4(0.2, 0.5, 1.0, 1.0);  // Color de la esfera
    }
    """

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

# Generar vértices para la esfera
def create_sphere(radius, segments):
    vertices = []
    for i in range(segments):
        theta = i * np.pi / segments
        for j in range(segments):
            phi = j * 2 * np.pi / segments
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.cos(theta)
            z = radius * np.sin(theta) * np.sin(phi)
            vertices.append([x, y, z])
    return np.array(vertices, dtype=np.float32)

# Dibujar una esfera
def draw_sphere(shader_program, sphere):
    model = glm.translate(glm.mat4(1.0), glm.vec3(*sphere.position))
    model = glm.scale(model, glm.vec3(sphere.radius))
    
    model_loc = glGetUniformLocation(shader_program, "model")
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))

    # Dibuja la esfera (usando el método de puntos, para simplicidad)
    glBegin(GL_POINTS)
    for vertex in create_sphere(sphere.radius, 20):  # 20 segmentos para la esfera
        glVertex3f(*vertex)
    glEnd()

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

    # Configurar esferas
    sphere1 = Sphere(position=[-1, 1, 0], velocity=[2, 0, 0], radius=1, mass=1.0)
    sphere2 = Sphere(position=[2, 1, 0], velocity=[-1, 0, 0], radius=1, mass=1.0)
    
    dt = 0.016  # Tiempo de paso (aproximadamente 60 FPS)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Actualizar simulación de física
        sphere1.update(dt)
        sphere2.update(dt)

        if sphere1.check_swept_collision(sphere2):
            sphere1.resolve_collision(sphere2)

        # Dibujar esferas
        draw_sphere(shader_program, sphere1)
        draw_sphere(shader_program, sphere2)

        glfw.swap_buffers(window)
        glfw.poll_events()
        time.sleep(dt)

    glfw.terminate()

if __name__ == "__main__":
    simulate_and_render()
