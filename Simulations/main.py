import tkinter as tk
import subprocess
from tkinter import messagebox

# Función para ejecutar el script de OpenGL
def ejecutar_visualizacion(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se ha podido ejecutar el script {script_name}.\nError: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")

# Función para crear un fondo degradado
def crear_fondo_degradado(canvas, color1, color2):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color)

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Aplicación para la visualización de fenómenos físicos")
ventana.geometry("600x500")

# Crear un canvas para el fondo degradado
canvas = tk.Canvas(ventana, width=600, height=500)
canvas.pack(fill="both", expand=True)

# Función para actualizar el fondo cuando la ventana se redimensiona
def actualizar_fondo(event):
    canvas.delete("all")
    crear_fondo_degradado(canvas, color_inici, color_fi)

# Asignar la función de actualización al cambio de tamaño de ventana
ventana.bind("<Configure>", actualizar_fondo)

# Colores para el degradado
color_inici = (135, 206, 250)  # Azul cielo
color_fi = (70, 130, 180)      # Azul acero

# Crear el fondo degradado
crear_fondo_degradado(canvas, color_inici, color_fi)

# Etiqueta de bienvenida
etiqueta_benvinguda = tk.Label(canvas, text="Visualizaciones de fenómenos físicos", font=("Arial", 18, "bold"), fg="white", bg="#4682B4", pady=10, padx=20)
etiqueta_benvinguda.place(relx=0.5, rely=0.1, anchor="center")

# Marco para agrupar los botones y que también se redimensione
marco_botones = tk.Frame(canvas, bg="#4682B4", bd=10, relief="ridge")
marco_botones.place(relx=0.5, rely=0.5, anchor="center")  # Cambiado al centro para ser responsivo

# Función para crear botones personalizados
def crear_boton(text, script_name):
    return tk.Button(marco_botones, text=text, width=30, height=2, font=("Arial", 12), bg="#87CEEB", fg="black",
                     activebackground="#4682B4", activeforeground="white", relief="flat",
                     command=lambda: ejecutar_visualizacion(script_name))

# Crear los botones
btn_100spheres = crear_boton("Game Simulation", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/cube_box.py")
btn_100spheres.pack(pady=5)

btn_acelerador = crear_boton("Colisión de Dos Esferas", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/two_spheres_colisioning.py")
btn_acelerador.pack(pady=5)

btn_dos_cubos = crear_boton("Colisión de Dos Cubos", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/two_cubes_colisioning.py")
btn_dos_cubos.pack(pady=5)

btn_salir = tk.Button(marco_botones, text="Salir", width=30, height=2, font=("Arial", 12), bg="#FF6347", fg="white",
                      activebackground="#CD5C5C", activeforeground="black", relief="flat",
                      command=ventana.quit)
btn_salir.pack(pady=20)

# Ejecutar la ventana principal
ventana.mainloop()


