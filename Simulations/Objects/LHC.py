import glm
import moderngl
import numpy as np

class LHC:
    def __init__(self, context, radius=1.0, tube_radius=0.2, position=(0, 0, 0)):
        self.ctx = context
        self.radius = radius
        self.tube_radius = tube_radius
        self.position = glm.vec3(position)

        # Configura blending para transparencia
        self.ctx.enable(moderngl.BLEND)

        # Configura shaders
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec3 in_position;
            uniform mat4 model;
            uniform mat4 projection;
            uniform mat4 view;
            void main() {
                gl_Position = projection * view * model * vec4(in_position, 1.0);
            }
            """,
            fragment_shader="""
            #version 330
            out vec4 fragColor;
            void main() {
                fragColor = vec4(1.0, 1.0, 1.0, 1.0);  // Blanco para el efecto de líneas
            }
            """
        )

        # Crea el mesh del toroide
        self.vertex_array = self.create_torus_mesh()

    def create_torus_mesh(self, segments=50, rings=50):
        vertices = []
        indices = []

        for i in range(segments):
            theta = 2 * np.pi * i / segments
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            for j in range(rings):
                phi = 2 * np.pi * j / rings
                cos_phi = np.cos(phi)
                sin_phi = np.sin(phi)

                x = (self.radius + self.tube_radius * cos_phi) * cos_theta
                y = (self.radius + self.tube_radius * cos_phi) * sin_theta
                z = self.tube_radius * sin_phi
                vertices.append((x, y, z))

                next_i = (i + 1) % segments
                next_j = (j + 1) % rings
                indices.extend([i * rings + j, i * rings + next_j])
                indices.extend([i * rings + j, next_i * rings + j])

        vertices = np.array(vertices, dtype='f4')
        indices = np.array(indices, dtype='i4')

        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        vao = self.ctx.vertex_array(self.program, [(vbo, '3f', 'in_position')], ibo)
        return vao

    def draw(self, projection_matrix, view_matrix):
        model_matrix = glm.translate(glm.mat4(1), self.position)
        self.program['model'].write(model_matrix)
        self.program['projection'].write(projection_matrix)
        self.program['view'].write(view_matrix)

        self.vertex_array.render(moderngl.LINES)
