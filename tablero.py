import pygame
import random as r
from config import BLACK, TAMAÑO_CUADROS, ESPACIO, FILAS, COLUMNAS, ANCHO, ALTO, BLUE, SIZE

# Agregar una estructura de datos para rastrear las casillas clickeadas
casillas_clickeadas = set()
barcos_ubicados = set()
barcos_enemigo = set()
click_enemigo = set()
# board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
# casillas_seleccionables = set()

# Reglas del juego de Batalla Naval
reglas_del_juego = [
    "Tipos de barcos:",
    "1. Lanchas (1 casilla)",
    "2. Submarinos (2 casillas)",
    "3. Buques (3 casillas)",
    "",
    "Reglas del Juego:",
    "1. Coloca tus barcos en el tablero, estos no pueden",
    "   ir en diagonal. El orden para posicionar es Lancha,", 
    "   Submarino y Buque",
    "2. Intenta adivinar la ubicación de los barcos",
    "   del oponente haciendo clic en las casillas.",
    "3. Gana el jugador que hunde todos los barcos",
    "   del oponente primero."
]

def is_in_barcos(casilla):
    for c in barcos_ubicados:
        if(c == casilla):
            return True
    return False

def is_in_list(casilla, casillas):
    for c in casillas:
        if(c == casilla):
            return True
    return False

def is_alround(casilla, casillas):
    print(casilla, casillas)
    if not casillas:
        return False
    if len(casillas) == 1:
        c = casillas[0]
        if (
            (casilla == (c[0] - 1, c[1])) or
            (casilla == (c[0] + 1, c[1])) or
            (casilla == (c[0], c[1] - 1)) or
            (casilla == (c[0], c[1] + 1)) or
            seleccion_diagonal(casilla, casillas)
        ):
            return True

    x_values = [c[0] for c in casillas]
    y_values = [c[1] for c in casillas]
    min_x, min_y, max_x, max_y = min(x_values), min(y_values), max(x_values), max(y_values)
    is_vertical = max_x - min_x == 0

    if is_vertical:
        if casilla[0] == min_x - 1 or casilla[0] == max_x + 1:
            return True
    else:
        if casilla[1] == min_y - 1 or casilla[1] == max_y + 1:
            return True

    return False


def seleccion_diagonal(casilla, casillas):
    for c in casillas:
        if(c == (casilla[0] -1, casilla[1] - 1)):
            return True
        elif(c == (casilla[0] + 1, casilla[1] + 1)):
            return True
        elif(c == (casilla[0] - 1, casilla[1] +1 )):
            return True
        elif(c == (casilla[0] +1 , casilla[1] - 1 )):
            return True
    return False

def inicializar_screen():
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("La Batalla Naval")
    return screen


def draw_board_with_ships(surface, title, x_offset, y_offset):
    element_x = 50
    element_y = 50  # Ajusta la posición vertical del tablero

    font = pygame.font.Font(None, 36)
    text = font.render(title, True, BLACK)
    text_rect = text.get_rect()
    text_rect.centerx = (
        element_x
        + (COLUMNAS * TAMAÑO_CUADROS + (COLUMNAS - 1) * ESPACIO) // 2
        + x_offset
    )
    text_rect.centery = element_y // 2 + y_offset  # Centra el título verticalmente

    surface.blit(text, text_rect)

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            x = element_x + col * (TAMAÑO_CUADROS + ESPACIO) + x_offset
            y = element_y + fila * (TAMAÑO_CUADROS + ESPACIO) + y_offset

            pygame.draw.rect(
                surface,
                BLACK,
                (x, y, TAMAÑO_CUADROS, TAMAÑO_CUADROS),
                1,
            )
            # Dibujar cuadrado azul
            if (fila, col) in barcos_ubicados:
                pygame.draw.rect(surface, BLUE, (x, y, TAMAÑO_CUADROS, TAMAÑO_CUADROS))

    # Reglas del juego

    reglas_rect = pygame.Rect(
    element_x + (COLUMNAS * TAMAÑO_CUADROS + (COLUMNAS - 1) * ESPACIO) + 20 + x_offset,
    element_y + y_offset,
    500,
    500  # Ajusta el tamaño del cuadro de reglas
    )
    pygame.draw.rect(surface, BLACK, reglas_rect, 2)

    # Dibuja las reglas en el cuadro de texto
    font = pygame.font.Font(None, 24)
    for i, regla in enumerate(reglas_del_juego):
        regla_text = font.render(regla, True, BLACK)
        regla_rect = regla_text.get_rect()
        regla_rect.topleft = (
            reglas_rect.left + 10,
            reglas_rect.top + 10 + i * 30  # Ajusta el espaciado vertical entre las reglas
        )
        surface.blit(regla_text, regla_rect)
        

    
    
def randomShips():
    # barcos_ubicados = set()
    ship_sizes = [3, 2, 1]
    
    for ship_size in ship_sizes:
        while True:
            orientation = r.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                x = r.randint(1, 10 - ship_size)  # Aseguramos que el barco quepa en el tablero
                y = r.randint(1, 10)
                new_ship = {(x + i, y) for i in range(ship_size)}
            else:
                x = r.randint(1, 10)
                y = r.randint(1, 10 - ship_size)
                new_ship = {(x, y + i) for i in range(ship_size)}
            
            # Verificamos que los barcos no se toquen
            if all(coord not in barcos_ubicados for coord in new_ship):
                barcos_ubicados.update(new_ship)
                break

    # return barcos_ubicados

def randomBoardSets():
    barcos_ubicados.clear()
    ships = {
        "p": [],
        "b": [],
        "s":[]
    }
    for tamano in [3, 2 ,1]:
        # print("tamano", tamano)
        while True:
            x = r.randint(0, SIZE - 1)
            y = r.randint(0, SIZE - 1)
            while(x + tamano >= SIZE):
                x = r.randint(0, SIZE - 1)
            while(y + tamano >= SIZE ):
                y = r.randint(0, SIZE - 1)
            direccion = r.choice(['horizontal', 'vertical'])

            if direccion == 'horizontal':
                if (x, y) in barcos_ubicados:
                    continue

                ocupado = False
                for i in range(tamano):
                    if (x + i, y) in barcos_ubicados:
                        ocupado = True
                        break

                if ocupado:
                    continue

                for i in range(tamano):     
                    if(i == 0):      
                        # print("entro i, tamano:", tamano)             
                        if(tamano == 3):
                            ships["s"] = [x, y + i, 1]
                        elif(tamano == 2):
                            ships["b"] = [x, y + i, 1]
                        else:
                            ships["p"] = [x, y+i, 1]
                    # positions_set.add((x + i, y))
                    barcos_ubicados.add((x, y+i))
            else:
                if (x, y) in barcos_ubicados:
                    continue

                ocupado = False
                for i in range(tamano):
                    if (x, y + i) in barcos_ubicados:
                        ocupado = True
                        break

                if ocupado:
                    continue

                for i in range(tamano):
                    if(i == 0):
                        if(tamano == 3):
                            ships["s"] = [x + i, y, 0]
                        elif(tamano == 2):
                            ships["b"] =[x + i, y, 0]
                        else:
                            ships["p"]=  [x+ i, y , 0]
                    # positions_set.add((x, y + i))
                    barcos_ubicados.add((x+ i, y ))

            break
    return ships

def draw_board_with_title(surface, title, x_offset, y_offset):
    element_x = 50
    element_y = 50  # Ajusta la posición vertical del tablero

    font = pygame.font.Font(None, 36)
    text = font.render(title, True, BLACK)
    text_rect = text.get_rect()
    text_rect.centerx = (
        element_x
        + (COLUMNAS * TAMAÑO_CUADROS + (COLUMNAS - 1) * ESPACIO) // 2
        + x_offset
    )
    text_rect.centery = element_y // 2 + y_offset  # Centra el título verticalmente

    surface.blit(text, text_rect)

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            x = element_x + col * (TAMAÑO_CUADROS + ESPACIO) + x_offset
            y = element_y + fila * (TAMAÑO_CUADROS + ESPACIO) + y_offset

            pygame.draw.rect(
                surface,
                BLACK,
                (x, y, TAMAÑO_CUADROS, TAMAÑO_CUADROS),
                1,
            )
            # Dibujar cuadrado azul
            if (fila, col) in barcos_ubicados:
                pygame.draw.rect(surface, BLUE, (x, y, TAMAÑO_CUADROS, TAMAÑO_CUADROS))

            # Dibujar una X en la casilla si está en la lista de casillas clickeadas
            if (fila, col) in click_enemigo:
                pygame.draw.line(
                    surface, BLACK, (x, y), (x + TAMAÑO_CUADROS, y + TAMAÑO_CUADROS), 2
                )
                pygame.draw.line(
                    surface, BLACK, (x + TAMAÑO_CUADROS, y), (x, y + TAMAÑO_CUADROS), 2
                )

def draw_board_with_title_enemy(surface, title, x_offset, y_offset):
    element_x = 50
    element_y = 50  # Ajusta la posición vertical del tablero

    font = pygame.font.Font(None, 36)
    text = font.render(title, True, BLACK)
    text_rect = text.get_rect()
    text_rect.centerx = (
        element_x
        + (COLUMNAS * TAMAÑO_CUADROS + (COLUMNAS - 1) * ESPACIO) // 2
        + x_offset
    )
    text_rect.centery = element_y // 2 + y_offset  # Centra el título verticalmente

    surface.blit(text, text_rect)

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            x = element_x + col * (TAMAÑO_CUADROS + ESPACIO) + x_offset
            y = element_y + fila * (TAMAÑO_CUADROS + ESPACIO) + y_offset

            pygame.draw.rect(
                surface,
                BLACK,
                (x, y, TAMAÑO_CUADROS, TAMAÑO_CUADROS),
                1,
            )
            # Dibujar cuadrado azul
            if (fila, col) in barcos_enemigo:
                pygame.draw.rect(surface, BLUE, (x, y, TAMAÑO_CUADROS, TAMAÑO_CUADROS))

            # Dibujar una X en la casilla si está en la lista de casillas clickeadas
            if (fila, col) in casillas_clickeadas:
                pygame.draw.line(
                    surface, BLACK, (x, y), (x + TAMAÑO_CUADROS, y + TAMAÑO_CUADROS), 2
                )
                pygame.draw.line(
                    surface, BLACK, (x + TAMAÑO_CUADROS, y), (x, y + TAMAÑO_CUADROS), 2
                )
