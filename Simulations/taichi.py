from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import time
import numpy
import math
import sys

# Estas definiciones existen en OpenGL.GL, pero no corresponden a las usadas aquí
GL_GEOMETRY_SHADER_EXT = 0x8DD9
GL_GEOMETRY_INPUT_TYPE_EXT = 0x8DDB
GL_GEOMETRY_OUTPUT_TYPE_EXT = 0x8DDC
GL_GEOMETRY_VERTICES_OUT_EXT = 0x8DDA

# 1: Define el método glProgramParameteri
_glProgramParameteri = None

def glProgramParameteri(program, pname, value):
    global _glProgramParameteri
    if not _glProgramParameteri:
        import ctypes
        gldll = ctypes.windll.opengl32
        prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_int)
        fptr = gldll.wglGetProcAddress('glProgramParameteriEXT')
        if fptr == 0:
            raise Exception("wglGetProcAddress('glProgramParameteriEXT') returned a zero address.")
        _glProgramParameteri = prototype(fptr)
    _glProgramParameteri(program, pname, value)

# 2: Define el método glCreateShaderObject
_glCreateShaderObject = None

def glCreateShaderObject(shadertype):
    global _glCreateShaderObject
    if not _glCreateShaderObject:
        import ctypes
        gldll = ctypes.windll.opengl32
        prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)
        fptr = gldll.wglGetProcAddress('glCreateShaderObjectARB')
        if fptr == 0:
            raise Exception("wglGetProcAddress('glCreateShaderObjectARB') returned a zero address.")
        _glCreateShaderObject = prototype(fptr)
    return _glCreateShaderObject(shadertype)

# Shader de vértices
vert = '''
void main() {
    gl_FrontColor = gl_Color;
    gl_Position = ftransform();
}
'''

# Shader de geometría
geom = '''
#version 120
#extension GL_EXT_geometry_shader4 : enable
const float radius = 0.5;
varying out vec2 coord;

void main() {
    gl_FrontColor = gl_FrontColorIn[0];
    coord = vec2(-1, -1);
    gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4(-radius, -radius, 0, 0));
    EmitVertex();

    coord = vec2(-1, 1);
    gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4(-radius, radius, 0, 0));
    EmitVertex();

    coord = vec2(1, -1);
    gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4(radius, -radius, 0, 0));
    EmitVertex();

    coord = vec2(1, 1);
    gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4(radius, radius, 0, 0));
    EmitVertex();
    EndPrimitive();
}
'''

# Shader de fragmentos
frag = '''
varying in vec2 coord;

void main() {
    vec4 color = gl_Color;
    color.a = 1.0 - length(coord);
    if (color.a < 0.0) discard;

    // Modelo de "iluminación" muy básico
    float d = dot(normalize(vec3(coord, 1.0)), vec3(0.19, 0.19, 0.96225));
    color.rgb *= d * d;

    // Fin del "iluminación"
    gl_FragColor = color;
}
'''

theta = 0.0
delta = 0.0
TIMEOUTFACTOR = 5.0

def my_idle():
    global theta, delta
    t = time.time()
    passed = t - delta
    theta += passed
    delta = t

    dirvector = numpy.array([-1 - (math.sin(theta / 2.0)), -1 - (math.cos(theta / 2.0)), 1.0])
    dirvector *= (1.0 / math.sqrt((dirvector ** 2).sum()))

    global POINTS, VEL, TIMES

    # Agregar "gravedad" a todas las velocidades
    VEL[:, 2] -= passed * 9.81 * 5

    # Incrementar posiciones según velocidades
    POINTS += passed * VEL

    pbelow_zero = POINTS[:, 2] < 0.0

    # "Arrastrar" todos los puntos debajo de cero (en z) hacia arriba de nuevo
    POINTS[pbelow_zero] *= [1, 1, 0]

    # Cambiar la velocidad z para todas las "colisiones" con el plano z cero
    VEL[pbelow_zero] *= [1, 1, -1.0]

    # Agregar segundos transcurridos a todos los tiempos de espera
    TIMES += passed
    timeouts = TIMES > TIMEOUTFACTOR
    TIMES[timeouts] = numpy.random.random(timeouts.sum()) * 0.1 * TIMEOUTFACTOR
    VEL[timeouts] = dirvector + 0.5 * numpy.random.random(timeouts.sum() * 3).reshape((-1, 3))
    VEL[timeouts] *= 50.0
    POINTS[timeouts] = [0.0, 0.0, 0.0]

    glutPostRedisplay()

shader_program = None

def define_shader():
    global shader_program
    shader_program = glCreateProgram()
    glProgramParameteri(shader_program, GL_GEOMETRY_INPUT_TYPE_EXT, GL.GL_POINTS)
    glProgramParameteri(shader_program, GL_GEOMETRY_OUTPUT_TYPE_EXT, GL.GL_TRIANGLE_STRIP)
    glProgramParameteri(shader_program, GL_GEOMETRY_VERTICES_OUT_EXT, 4)

    vobj = glCreateShaderObject(GL_VERTEX_SHADER)
    glShaderSource(vobj, vert)
    glCompileShader(vobj)
    print(glGetShaderInfoLog(vobj))

    glAttachShader(shader_program, vobj)

    gobj = glCreateShaderObject(GL_GEOMETRY_SHADER_EXT)
    glShaderSource(gobj, geom)
    glCompileShader(gobj)
    print(glGetShaderInfoLog(gobj))

    glAttachShader(shader_program, gobj)

    fobj = glCreateShaderObject(GL_FRAGMENT_SHADER)
    glShaderSource(fobj, frag)
    glCompileShader(fobj)
    print(glGetShaderInfoLog(fobj))

    glAttachShader(shader_program, fobj)
    glLinkProgram(shader_program)
    print(glGetProgramInfoLog(shader_program))

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(65.0, width / float(height), 1, 1000)
    glMatrixMode(GL_MODELVIEW)

POINTS = None
COLORS = None
VEL = None
TIMES = None

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(60.0, 60.0, 25.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    glTranslatef(25.0, 25.0, 0)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glUseProgram(shader_program)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)

    glColorPointer(3, GL_FLOAT, 0, COLORS)
    glVertexPointer(3, GL_FLOAT, 0, POINTS)
    glDrawArrays(0, 0, len(POINTS))

    glutSwapBuffers()

def init():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
    glutInitWindowSize(1280, 720)
    glutCreateWindow("Glut test window")
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(my_idle)
    glEnable(GL_DEPTH_TEST)
    glClearColor(1, 1, 1, 0)
    define_shader()

    # 100k bolas
    count = 100000
    global POINTS, COLORS, VEL, TIMES

    COLORS = numpy.random.random(count * 3).reshape((-1, 3))
    POINTS = 100000 * numpy.ones(count * 3).reshape((-1, 3))
    VEL = numpy.zeros(count * 3).reshape((-1, 3))
    TIMES = numpy.random.random(count) * TIMEOUTFACTOR

    glutMainLoop()

if __name__ == "__main__":
    init()

