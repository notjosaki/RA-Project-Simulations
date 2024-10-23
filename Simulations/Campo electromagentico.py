import moderngl
import numpy as np
import glm
import pyrr
from pyrr import Matrix44
import pygame
from pygame.locals import *
from Objects.sphere3 import Photon,Electron,Proton

# Inicializar pygame y la ventana de OpenGL
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Simulación de partículas: Electrón, Protón y Fotón")

# Crear el contexto de ModernGL
ctx = moderngl.create_context()

# Shader de vértices
vertex_shader_code = """
#version 330
in vec3 in_vert;
uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;
void main() {
    gl_Position = proj * view * model * vec4(in_vert, 1.0);
}
"""

# Shader de fragmentos
fragment_shader_code = """
#version 330
out vec4 fragColor;
uniform vec3 color;
void main() {
    fragColor = vec4(color, 1.0);
}
"""

# Programa de shaders
prog = ctx.program(vertex_shader=vertex_shader_code, fragment_shader=fragment_shader_code)

# Definir una esfera como representación de las partículas
def create_sphere(radius, sectors, stacks):
    vertices = []
    for i in range(stacks + 1):
        stack_angle = np.pi / 2 - i * np.pi / stacks
        xy = radius * np.cos(stack_angle)
        z = radius * np.sin(stack_angle)

        for j in range(sectors + 1):
            sector_angle = j * 2 * np.pi / sectors
            x = xy * np.cos(sector_angle)
            y = xy * np.sin(sector_angle)
            vertices.append([x, y, z])
    return np.array(vertices, dtype='f4')

# Crear las esferas para las partículas
sphere_vertices = create_sphere(10, 20, 20)

# Cargar los vértices en un VBO (Vertex Buffer Object)
vbo = ctx.buffer(sphere_vertices.flatten().tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

# Configuración de la cámara
proj = Matrix44.perspective_projection(45.0, 800 / 600, 0.1, 100.0)
view = Matrix44.look_at(
    eye=(0.0, 0.0, 3.0),
    target=(0.0, 0.0, 0.0),
    up=(0.0, 1.0, 0.0),
)

# Variables de simulación
electron = Electron(position=[-1, 0, 0], velocity=[0.01, 0, 0])
proton = Proton(position=[1, 0, 0], velocity=[-0.01, 0, 0])
photon = Photon(position=[0, 0, 0], velocity=[0, 0.01, 0])

# Reloj para medir el tiempo
clock = pygame.time.Clock()

# Bucle principal
running = True
while running:
    # Procesar eventos de Pygame
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    
    # Actualizar la simulación
    dt = clock.tick(60) / 1000.0
    electron.update(dt)
    proton.update(dt)
    photon.update(dt)

    # Aplicar fuerzas electromagnéticas
    force_electron_proton = electron.apply_electromagnetic_force(proton)
    electron.apply_force(force_electron_proton, dt)
    proton.apply_force(-force_electron_proton, dt)

    # Limpiar la pantalla
    ctx.clear(0.1, 0.1, 0.1)

    # Dibujar las partículas (esferas)
    prog['model'].write(pyrr.matrix44.create_from_translation(electron.position).astype('f4').tobytes())
    prog['color'].write(np.array([0.0, 0.0, 1.0], dtype='f4'))  # Color azul para el electrón
    vao.render(moderngl.POINTS)

    prog['model'].write(pyrr.matrix44.create_from_translation(proton.position).astype('f4').tobytes())
    prog['color'].write(np.array([1.0, 0.0, 0.0], dtype='f4'))  # Color rojo para el protón
    vao.render(moderngl.POINTS)

    prog['model'].write(pyrr.matrix44.create_from_translation(photon.position).astype('f4').tobytes())
    prog['color'].write(np.array([1.0, 1.0, 0.0], dtype='f4'))  # Color amarillo para el fotón
    vao.render(moderngl.POINTS)

    # Actualizar la ventana
    pygame.display.flip()

# Cerrar Pygame
pygame.quit()
