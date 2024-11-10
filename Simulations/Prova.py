import pygame
from pygame.locals import *
import glm
import moderngl
from Objects.LHC import LHC

# Configuración de Pygame y moderngl
def main():
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    ctx = moderngl.create_context()

    # Configuración de la cámara
    fov = 45
    aspect_ratio = 800 / 600
    projection = glm.perspective(glm.radians(fov), aspect_ratio, 0.1, 100.0)
    camera_pos = glm.vec3(0.0, 0.0, 15.0)
    view = glm.lookAt(camera_pos, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

    # Creación del objeto LHC
    lhc = LHC(ctx)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Limpiar el contexto con color negro
        ctx.clear(0.0, 0.0, 0.0)
        
        # Dibujar el objeto LHC
        lhc.draw(projection, view)
        
        # Actualizar la pantalla
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
