import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

class Box:
    def __init__(self, center, size, shape="cube", material="elastic", energy_loss=0.9):
        self.center = np.array(center)  # Centro de la caja delimitadora
        self.size = size  # Tamaño de la caja (cubo) o radio (esfera)
        self.shape = shape  # "cube" para cubo, "sphere" para delimitador esférico
        self.material = material  # Material de la caja, puede afectar el rebote
        self.energy_loss = energy_loss  # Factor de pérdida de energía en colisión

    def draw(self):
        """Renderiza la caja o delimitador redondo."""
        glPushMatrix()
        glTranslatef(*self.center)
        if self.shape == "cube":
            glutWireCube(self.size * 2)
        elif self.shape == "sphere":
            glutWireSphere(self.size, 20, 20)
        glPopMatrix()

    def collide(self, sphere_pos, sphere_vel):
        """Calcula la colisión de una esfera con el delimitador."""
        if self.shape == "cube":
            for i in range(3):
                if abs(sphere_pos[i] - self.center[i]) >= self.size:
                    sphere_vel[i] *= -self.energy_loss  # Rebote con pérdida de energía
        elif self.shape == "sphere":
            dist_to_center = np.linalg.norm(sphere_pos - self.center)
            if dist_to_center >= self.size:
                normal = (sphere_pos - self.center) / dist_to_center
                sphere_vel -= 2 * np.dot(sphere_vel, normal) * normal
                sphere_vel *= self.energy_loss  # Aplica la pérdida de energía

        return sphere_vel

# Uso de la clase Box con una esfera:
box = Box(center=(0, 0, 0), size=10, shape="cube", material="elastic", energy_loss=0.8)

# En el bucle de renderizado:
sphere_pos = np.array([5.0, 5.0, 5.0])
sphere_vel = np.array([1.0, -2.0, 1.5])

# Al detectar la colisión, actualizamos la velocidad
sphere_vel = box.collide(sphere_pos, sphere_vel)
