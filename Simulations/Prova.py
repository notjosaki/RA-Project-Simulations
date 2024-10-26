# import numpy as np
# import glm
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# import time

# # Definición de la clase Box para los rebotes con pérdida de energía
# class Box:
#     def __init__(self, center, size, energy_loss=0.9):
#         self.center = np.array(center, dtype=np.float64)
#         self.size = size  # tamaño del cubo
#         self.energy_loss = energy_loss  # pérdida de energía en cada rebote

#     def draw(self):
#         glPushMatrix()
#         glTranslatef(*self.center)
#         glutWireCube(self.size * 2)
#         glPopMatrix()

#     def collide(self, sphere):
#         """Detecta colisiones con las paredes de la caja y ajusta la velocidad de la esfera."""
#         for i in range(3):  # Comprueba cada eje (x, y, z)
#             if abs(sphere.position[i] - self.center[i]) + sphere.radius >= self.size:
#                 sphere.velocity[i] = -sphere.velocity[i] * self.energy_loss  # Rebote con pérdida de energía

# # Clase Sphere (reutilizando tu implementación)
# class Sphere:
#     def __init__(self, position, velocity, radius, mass=1.0):
#         self.position = np.array(position, dtype=np.float64)
#         self.velocity = np.array(velocity, dtype=np.float64)
#         self.radius = radius
#         self.mass = mass

#     def update(self, dt):
#         """Actualiza la posición de la esfera."""
#         self.position += self.velocity * dt

#     def draw(self):
#         glPushMatrix()
#         glTranslatef(*self.position)
#         glutWireSphere(self.radius, 16, 16)
#         glPopMatrix()

# # Función principal para simular el rebote
# def main():
#     # Inicialización de OpenGL
#     glutInit()
#     glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
#     glutInitWindowSize(800, 600)
#     glutCreateWindow(b'Rebote en caja')

#     glEnable(GL_DEPTH_TEST)

#     # Crear objetos
#     box = Box(center=(0, 0, 0), size=10, energy_loss=0.8)
#     sphere = Sphere(position=(1, 2, 3), velocity=(1, -1.5, 1.2), radius=0.5)

#     def display():
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#         glLoadIdentity()
#         gluLookAt(20, 20, 20, 0, 0, 0, 0, 1, 0)

#         # Dibujar la caja y la esfera
#         box.draw()
#         sphere.draw()

#         # Actualizar la pantalla
#         glutSwapBuffers()

#     def update(dt):
#         sphere.update(dt)
#         box.collide(sphere)  # Comprobar colisiones y aplicar rebote

#         # Redibujar la escena
#         glutPostRedisplay()

#     # Bucle de animación
#     last_time = time.time()
#     def animate():
#         nonlocal last_time
#         current_time = time.time()
#         dt = current_time - last_time
#         update(dt)
#         last_time = current_time
#         glutTimerFunc(16, lambda _: animate(), 0)

#     # Asignar funciones de dibujo y animación
#     glutDisplayFunc(display)
#     animate()

#     glutMainLoop()

# if __name__ == "__main__":
#     main()

from OpenGL.GLUT import glutInit

try:
    glutInit()  # Esto debería funcionar sin error
    print("GLUT inicializado correctamente.")
except Exception as e:
    print(f"Error al inicializar GLUT: {e}")

