import pygame
import sys
import lhc_oval_creatiu


# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("SIMULADOR LHC")

# Colores
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)
AZUL_OSCURO = (0, 0, 128)
AZUL_CLARO = (70, 130, 180)
GRIS_OSCURO = (100, 100, 100)
COLOR_BOTON = (30, 144, 255)
COLOR_BOTON_HOVER = (0, 191, 255)
COLOR_BOTON_SALIR = (150, 50, 50)
COLOR_BOTON_SALIR_HOVER = (200, 0, 0)
BLANCO = (255, 255, 255)

# Gradiente de fondo
def crear_gradiente(superficie, color1, color2):
    for y in range(ALTO):
        r = int(color1[0] + (color2[0] - color1[0]) * y / ALTO)
        g = int(color1[1] + (color2[1] - color1[1]) * y / ALTO)
        b = int(color1[2] + (color2[2] - color1[2]) * y / ALTO)
        pygame.draw.line(superficie, (r, g, b), (0, y), (ANCHO, y))

# Fuentes
fuente_titulo = pygame.font.SysFont("Impact", 48)
fuente_boton = pygame.font.SysFont("Arial", 42, bold=True)

# Función para dibujar un botón
def dibujar_boton(texto, rect, color_fondo, color_texto, hover=False, hover_color=None):
    color_final = hover_color if hover and hover_color else (COLOR_BOTON_HOVER if hover else color_fondo)
    pygame.draw.rect(pantalla, color_final, rect, border_radius=15)
    texto_superficie = fuente_boton.render(texto, True, color_texto)
    texto_rect = texto_superficie.get_rect(center=rect.center)
    pantalla.blit(texto_superficie, texto_rect)

# Función principal del menú
def menu_principal():
    while True:
        crear_gradiente(pantalla, (100, 149, 237), (240, 248, 255))

        # Título
        titulo = fuente_titulo.render("Simulador de Fenòmens Físics", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

        # Botones más anchos
        boton_creacio = pygame.Rect(200, 200, 400, 70)
        boton_simulacio = pygame.Rect(200, 300, 400, 70)
        boton_salir = pygame.Rect(200, 400, 400, 70)

        # Detectar hover
        mouse_pos = pygame.mouse.get_pos()
        hover_creacio = boton_creacio.collidepoint(mouse_pos)
        hover_simulacio = boton_simulacio.collidepoint(mouse_pos)
        hover_salir = boton_salir.collidepoint(mouse_pos)

        dibujar_boton("Mode de Creació", boton_creacio, COLOR_BOTON, BLANCO, hover=hover_creacio)
        dibujar_boton("Mode de Simulació", boton_simulacio, COLOR_BOTON, BLANCO, hover=hover_simulacio)
        dibujar_boton("Sortir", boton_salir, COLOR_BOTON_SALIR, BLANCO, hover=hover_salir, hover_color=COLOR_BOTON_SALIR_HOVER)

        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_creacio.collidepoint(evento.pos):
                    lhc_oval_creatiu.main()
                if boton_simulacio.collidepoint(evento.pos):
                    mode_simulacio()
                if boton_salir.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

# Función para el modo de creación
def mode_creacio():
    while True:
        crear_gradiente(pantalla, (100, 149, 237), (240, 248, 255))

        # Título
        titulo = fuente_titulo.render("Mode de Creació", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

        # Botón de regreso
        boton_regresar = pygame.Rect(250, 500, 300, 70)
        mouse_pos = pygame.mouse.get_pos()
        hover_regresar = boton_regresar.collidepoint(mouse_pos)
        dibujar_boton("Tornar", boton_regresar, GRIS_OSCURO, BLANCO, hover=hover_regresar)

        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_regresar.collidepoint(evento.pos):
                    return

        pygame.display.flip()

# Función para el modo de simulación
def mode_simulacio():
    while True:
        crear_gradiente(pantalla, (100, 149, 237), (240, 248, 255))

        # Título
        titulo = fuente_titulo.render("Mode de Simulació", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

        # Botón de regreso
        boton_regresar = pygame.Rect(250, 500, 300, 70)
        mouse_pos = pygame.mouse.get_pos()
        hover_regresar = boton_regresar.collidepoint(mouse_pos)
        dibujar_boton("Tornar", boton_regresar, GRIS_OSCURO, BLANCO, hover=hover_regresar)

        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_regresar.collidepoint(evento.pos):
                    return

        pygame.display.flip()

# Iniciar el programa
menu_principal()
