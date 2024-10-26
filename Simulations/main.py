import tkinter as tk
import subprocess
from tkinter import messagebox

# Funció per executar el script de OpenGL
def ejecutar_visualizacion(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No s'ha pogut executar el script {script_name}.\nError: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperat: {e}")

# Funció per crear un fons degradat
def crear_fondo_degradat(canvas, color1, color2):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    for i in range(height):
        # Calcula el color intermedi
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color)

# Crear finestra principal
ventana = tk.Tk()
ventana.title("Aplicació per a la visualització de fenòmens físics")
ventana.geometry("600x500")

# Crear un canvas per al fons degradat
canvas = tk.Canvas(ventana, width=600, height=500)
canvas.pack(fill="both", expand=True)

# Colors per al degradat
color_inici = (135, 206, 235)  # Cel blau clar
color_fi = (240, 255, 255)     # Blanc

# Crear el fons degradat
crear_fondo_degradat(canvas, color_inici, color_fi)

# Etiqueta de benvinguda
etiqueta_benvinguda = tk.Label(ventana, text="Visualitzacions de fenòmens físics", font=("Arial", 16), bg="#87CEEB")
etiqueta_benvinguda.pack(pady=20)

# Marc per a agrupar els botons
marco_botones = tk.Frame(ventana, bg="#87CEEB")
marco_botones.pack(pady=10)

# Funció per crear botons
def crear_boton(text, script_name):
    return tk.Button(marco_botones, text=text, width=30, bg="#ADD8E6", 
                     command=lambda: ejecutar_visualizacion(script_name))

# Crear els botons
btn_100spheres = crear_boton("100 Esferes Rebotant", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/100spheres_bouncing.py")
btn_100spheres.pack(pady=5)

btn_acelerador = crear_boton("Col·lisió de Dues Esferes", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/two_spheres_colisioning.py")
btn_acelerador.pack(pady=5)

btn_dos_cubos = crear_boton("Col·lisió de Dues Cubs", "C:/Users/figue/Documents/UAB/UAB/Setè Quatri/Projecte RA/RA-Project-Simulations/Simulations/two_cubes_colisioning.py")
btn_dos_cubos.pack(pady=5)

btn_salir = tk.Button(ventana, text="Sortir", width=30, bg="#ADD8E6", command=ventana.quit)
btn_salir.pack(pady=20)

# Executar la finestra principal
ventana.mainloop()


