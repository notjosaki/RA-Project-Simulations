import numpy as np
import glm
import moderngl
import pygame
from pygame.locals import *
from OpenGL.GL import *  # Importa las funciones de OpenGL
from pyrr import Matrix44
from Objects.Particles import Electron
from Objects.iman import Iman

# Inicializar pygame y la ventana de OpenGL
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Simulación de Campo Electromagnético")

