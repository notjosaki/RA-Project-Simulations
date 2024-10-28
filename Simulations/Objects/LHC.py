import glm
import moderngl
import numpy as np

class LDR:
    def __init__(self, context, length=10.0, radius=1.0, position=(0, 0, 0)):
        """
        Inicialitza l'accelerador de partícules representat com un tub.
        :param context: el context de moderngl per renderitzar el tub.
        :param length: longitud del tub.
        :param radius: radi del tub.
        :param position: posició del centre del tub en l'espai 3D.
        """
        self.ctx = context
        self.length = length
        self.radius = radius
        self.position = glm.vec3(position)

        # Crea el mesh del tub
        self.vertex_array = self.create_cylinder_mesh()

        # Configura shaders (vertex, fragment) per visualització
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
                fragColor = vec4(0.3, 0.7, 0.9, 1.0);  // Color blau per representar el tub
            }
            """
        )

    def create_cylinder_mesh(self, segments=50):
        """
        Crea el mesh del cilindre que representa el tub de l'accelerador.
        :param segments: nombre de segments per aproximar el cilindre.
        :return: un Vertex Array Object (VAO) per al cilindre.
        """
        vertices = []
        indices = []
        
        # Crea els punts per als cercles superior i inferior
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = np.cos(angle) * self.radius
            y = np.sin(angle) * self.radius
            # Cercle inferior
            vertices.append((x, y, -self.length / 2))
            # Cercle superior
            vertices.append((x, y, self.length / 2))
            
            # Índexs per a quads que formen el cilindre
            if i < segments - 1:
                indices.extend([2 * i, 2 * i + 1, 2 * i + 2])
                indices.extend([2 * i + 1, 2 * i + 3, 2 * i + 2])
            else:
                # Connecta l'últim segment amb el primer
                indices.extend([2 * i, 2 * i + 1, 0])
                indices.extend([2 * i + 1, 1, 0])

        # Converteix a arrays NumPy per renderitzar
        vertices = np.array(vertices, dtype='f4')
        indices = np.array(indices, dtype='i4')
        
        # Crea buffers i vertex array object (VAO)
        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        vao = self.ctx.vertex_array(self.program, [(vbo, '3f', 'in_position')], ibo)
        return vao

    def draw(self, projection_matrix, view_matrix):
        """
        Dibuixa el tub a l'escena.
        :param projection_matrix: matriu de projecció per a la càmera.
        :param view_matrix: matriu de vista per a la càmera.
        """
        # Defineix la matriu de model per posicionar el tub en l'espai
        model_matrix = glm.translate(glm.mat4(1), self.position)

        # Carrega les matrius en els uniforms del shader
        self.program['model'].write(model_matrix)
        self.program['projection'].write(projection_matrix)
        self.program['view'].write(view_matrix)

        # Dibuixa el cilindre
        self.vertex_array.render(moderngl.TRIANGLES)
