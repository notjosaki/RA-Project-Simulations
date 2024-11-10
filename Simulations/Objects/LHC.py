import glm
import moderngl
import numpy as np

class LHC:
    def __init__(self, context, length=20.0, radius=1.0, position=(0, 0, 0)):
        self.ctx = context
        self.length = length
        self.radius = radius
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
                fragColor = vec4(0.3, 0.7, 0.9, 0.3);  // Azul con 30% de opacidad
            }
            """
        )

        # Crea el mesh del cilindro
        self.vertex_array = self.create_cylinder_mesh()

    def create_cylinder_mesh(self, segments=50):
        vertices = []
        indices = []
        
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = np.cos(angle) * self.radius
            y = np.sin(angle) * self.radius
            vertices.append((x, y, -self.length / 2))
            vertices.append((x, y, self.length / 2))
            
            if i < segments - 1:
                indices.extend([2 * i, 2 * i + 1, 2 * i + 2])
                indices.extend([2 * i + 1, 2 * i + 3, 2 * i + 2])
            else:
                indices.extend([2 * i, 2 * i + 1, 0])
                indices.extend([2 * i + 1, 1, 0])

        vertices = np.array(vertices, dtype='f4')
        indices = np.array(indices, dtype='i4')
        
        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        vao = self.ctx.vertex_array(self.program, [(vbo, '3f', 'in_position')], ibo)
        return vao

    def draw(self, projection_matrix, view_matrix):
        model_matrix = glm.translate(glm.mat4(1), self.position)
        model_matrix = glm.scale(model_matrix, glm.vec3(10.0, 1.0, 1.0))  # Escala para alargar el cilindro

        self.program['model'].write(model_matrix)
        self.program['projection'].write(projection_matrix)
        self.program['view'].write(view_matrix)

        self.vertex_array.render(moderngl.TRIANGLES)
