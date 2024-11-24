import tkinter as tk
from tkinter import messagebox
import subprocess

# Función para ejecutar el script de OpenGL
def ejecutar_visualizacion(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se ha podido ejecutar el script {script_name}.\nError: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")

# Función para crear un fondo degradado animado
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
ventana.geometry("600x600")
ventana.resizable(False, False)

# Crear un canvas para el fondo degradado
canvas = tk.Canvas(ventana, width=600, height=600)
canvas.pack(fill="both", expand=True)

# Función para actualizar el fondo cuando la ventana se redimensiona
def actualizar_fondo(event):
    canvas.delete("all")
    crear_fondo_degradado(canvas, color_inici, color_fi)

# Asignar la función de actualización al cambio de tamaño de ventana
ventana.bind("<Configure>", actualizar_fondo)

# Colores para el degradado (más vivos)
color_inici = (131, 221, 205)  # Aqua (turquesa brillante)
color_fi = (12, 88, 155)       # Magenta (fucsia)

# Crear el fondo degradado
crear_fondo_degradado(canvas, color_inici, color_fi)

# Etiqueta de bienvenida con una tipografía de estilo videojuego
etiqueta_benvinguda = tk.Label(canvas, text="Simulacions de fenòmens físics", font=("Press Start 2P", 20, "bold"), fg="white", bg="#4682B4", pady=15, padx=30)
etiqueta_benvinguda.place(relx=0.5, rely=0.1, anchor="center")

# Marco para agrupar los botones
marco_botones = tk.Frame(canvas, bg="#4682B4", bd=10, relief="ridge", padx=10, pady=10)
marco_botones.place(relx=0.5, rely=0.6, anchor="center")  # Ajusta el valor de relx para mover el marco más abajo

# Función para crear botones personalizados con efecto hover y sombras
def crear_boton(text, script_name):
    boton = tk.Button(marco_botones, text=text, width=30, height=2, font=("Press Start 2P", 12, "bold"), bg="#87CEEB", fg="black",
                      activebackground="#4682B4", activeforeground="white", relief="flat",
                      command=lambda: ejecutar_visualizacion(script_name), bd=5)

    # Efecto de hover: Cambia el color de fondo cuando el ratón entra y sale
    boton.bind("<Enter>", lambda e: boton.config(bg="#5F9EA0", fg="white"))
    boton.bind("<Leave>", lambda e: boton.config(bg="#87CEEB", fg="black"))

    # Añadir sombra al botón
    boton.bind("<ButtonPress>", lambda e: boton.config(relief="sunken"))
    boton.bind("<ButtonRelease>", lambda e: boton.config(relief="raised"))

    return boton

# Crear los botones con estilo de videojuego
btn_100spheres = crear_boton("Simulació Malla Gravitacional", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/RA-Project-Simulations/Simulations/Planet_Malla.py")
btn_100spheres.pack(pady=5)

btn_100spheres = crear_boton("Simulació Cub Gravitacional", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/RA-Project-Simulations/Simulations/Planet_Simulation.py")
btn_100spheres.pack(pady=5)

btn_100spheres = crear_boton("Simulació Partícules Cub", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/RA-Project-Simulations/Simulations/new_cube_box.py")
btn_100spheres.pack(pady=5)

btn_acelerador = crear_boton("LHC Primera Versio", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/RA-Project-Simulations/Simulations/lhc_box.py")
btn_acelerador.pack(pady=5)

btn_dos_cubos = crear_boton("LHC Realista", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/RA-Project-Simulations/Simulations/lhc_oval.py")
btn_dos_cubos.pack(pady=5)

# Botón de salida con efecto hover
btn_salir = tk.Button(marco_botones, text="Salir", width=30, height=2, font=("Press Start 2P", 12, "bold"), bg="#FF6347", fg="white",
                      activebackground="#CD5C5C", activeforeground="black", relief="flat",
                      command=ventana.quit)
btn_salir.pack(pady=20)
btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg="#CD5C5C"))
btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg="#FF6347"))

# Ejecutar la ventana principal
ventana.mainloop()
