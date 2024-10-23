import tkinter as tk
import subprocess

# Función para ejecutar el script de OpenGL
def ejecutar_visualizacion(script_name):
    try:
        subprocess.run(["python", script_name])
    except Exception as e:
        print(f"Error ejecutando el script {script_name}: {e}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Applicacio per la visualització de fenomens fisics")
ventana.geometry("600x500")
ventana.configure(bg="#87CEEB")  # Fondo 

# Etiqueta de bienvenida
etiqueta_bienvenida = tk.Label(ventana, text="Visualizacions de fenomens fisics", font=("Arial", 16), bg="#87CEEB")
etiqueta_bienvenida.pack(pady=20)


btn_100spheres = tk.Button(ventana, text="100 Esferas Rebotando", width=30, bg="#ADD8E6", command=lambda: ejecutar_visualizacion("Simulations/100spheres_bouncing.py"))
btn_100spheres.pack(pady=10)

btn_acelerador = tk.Button(ventana, text="Acelerador de Partículas", width=30, bg="#ADD8E6", command=lambda: ejecutar_visualizacion("Simulations/Accelerador_de_particules.py"))
btn_acelerador.pack(pady=10)

btn_dos_cubos = tk.Button(ventana, text="Colisión de Dos Cubos", width=30, bg="#ADD8E6", command=lambda: ejecutar_visualizacion("Simulations/two_cubes_colisioning.py"))
btn_dos_cubos.pack(pady=10)


btn_salir = tk.Button(ventana, text="Salir", width=30, bg="#ADD8E6", command=ventana.quit)
btn_salir.pack(pady=20)

# Ejecutar la ventana principal
ventana.mainloop()
