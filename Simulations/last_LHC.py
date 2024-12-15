import moderngl
import numpy as np
from pyrr import Matrix44
import glfw

# Initialize GLFW
def init_window(width, height, title):
    if not glfw.init():
        raise Exception("GLFW initialization failed")

    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")

    glfw.make_context_current(window)
    return window

# Define the vertex and fragment shaders
VERTEX_SHADER = """
#version 330 core
in vec3 in_position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
out vec3 frag_color;
void main() {
    frag_color = vec3(0.5, 0.8, 1.0);
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 frag_color;
out vec4 color;
void main() {
    color = vec4(frag_color, 1.0);
}
"""

def generate_oval_tube(radius_x, radius_y, length, segments):
    vertices = []
    for i in range(segments):
        theta = 2 * np.pi * i / segments
        x = radius_x * np.cos(theta)
        y = radius_y * np.sin(theta)
        vertices.append([x, y, -length / 2])
        vertices.append([x, y, length / 2])
    return np.array(vertices, dtype='f4')

# Main application
class LHCSimulation:
    def __init__(self):
        self.width, self.height = 800, 600
        self.window = init_window(self.width, self.height, "LHC Simulation")
        self.ctx = moderngl.create_context()
        self.prog = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        # Generate oval tube geometry
        self.vertices = generate_oval_tube(2.0, 1.0, 5.0, 100)
        self.vbo = self.ctx.buffer(self.vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

        # Matrices
        self.model = Matrix44.identity(dtype='f4')
        self.view = Matrix44.look_at(
            eye=[5.0, 5.0, 5.0],
            target=[0.0, 0.0, 0.0],
            up=[0.0, 1.0, 0.0],
            dtype='f4',
        )
        self.projection = Matrix44.perspective_projection(45.0, self.width / self.height, 0.1, 100.0, dtype='f4')

        self.current_view = 0  # Tracks the current view index
        self.views = [
            Matrix44.look_at([5.0, 5.0, 5.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], dtype='f4'),  # Isometric
            Matrix44.look_at([0.0, 5.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, -1.0], dtype='f4'),  # Top view
            Matrix44.look_at([0.0, 0.0, 5.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], dtype='f4'),  # Front view
        ]

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.handle_input()
            self.render()
        glfw.terminate()

    def handle_input(self):
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.PRESS:
            self.current_view = (self.current_view + 1) % len(self.views)
            self.view = self.views[self.current_view]

    def render(self):
        self.ctx.clear(0.1, 0.1, 0.1)
        self.prog['model'].write(self.model)
        self.prog['view'].write(self.view)
        self.prog['projection'].write(self.projection)
        self.vao.render(moderngl.LINES)
        glfw.swap_buffers(self.window)

if __name__ == "__main__":
    simulation = LHCSimulation()
    simulation.run()
