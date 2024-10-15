import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
import random

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

# --- Sphere class with simple physics ---
class Sphere:
    def __init__(self, position, velocity, radius):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.radius = radius

    def update(self, dt):
        self.position += self.velocity * dt
        # Add simple gravity (if y is downwards)
        self.velocity[1] -= 9.81 * dt

        # Bounce on the ground (y=0 plane)
        if self.position[1] - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = -self.velocity[1] * 0.9  # Energy loss

    def check_collision(self, other):
        distance = np.linalg.norm(self.position - other.position)
        return distance < self.radius + other.radius

def resolve_collision(sphere1, sphere2):
    # Simple elastic collision response
    normal = sphere2.position - sphere1.position
    normal = normal / np.linalg.norm(normal)  # Normalize

    relative_velocity = sphere1.velocity - sphere2.velocity
    velocity_along_normal = np.dot(relative_velocity, normal)

    if velocity_along_normal > 0:
        return

    # Elastic collision resolution
    restitution = 0.9
    j = -(1 + restitution) * velocity_along_normal
    j /= (1 / sphere1.radius + 1 / sphere2.radius)

    impulse = j * normal
    sphere1.velocity -= impulse / sphere1.radius
    sphere2.velocity += impulse / sphere2.radius

def create_texture(path):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    image = pygame.image.load(path)
    image = pygame.transform.flip(image, False, True)  # Flip for OpenGL coordinates
    image_data = pygame.image.tostring(image, "RGB")
    width, height = image.get_size()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    return texture

# --- Initialization code ---
def create_sphere():
    # For simplicity, use a UV-sphere algorithm
    latitudes = 30
    longitudes = 30
    radius = 1.0
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

# --- Main loop ---
def main():
    # Initialize Pygame and OpenGL
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('OpenGL Physics Simulation')

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Compile shaders
    shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                            compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    glUseProgram(shader)

    # Generate sphere data
    vertices, tex_coords, indices = create_sphere()

    # VAO and VBO setup
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

    # Load texture
    texture = create_texture('Textures/t1.avif.jpg')
    glUniform1i(glGetUniformLocation(shader, "texture1"), 0)

    # Camera and projection setup
    view = glm.lookAt(glm.vec3(0, 5, 10), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    projection = glm.perspective(glm.radians(45), 800 / 600, 0.1, 100)

    # Create multiple spheres
    spheres = [Sphere([random.uniform(-10, 10), random.uniform(5, 10), random.uniform(-10, 10)],
                      [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)], 1.0)
               for _ in range(1000)]

    clock = pygame.time.Clock()

    # Main render loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Simulate and render spheres
        for i, sphere in enumerate(spheres):
            sphere.update(dt)

            # Model matrix for each sphere
            model = glm.translate(glm.mat4(1.0), glm.vec3(*sphere.position))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
            glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

            # Draw sphere
            glBindVertexArray(vao)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture)
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()


