import pygame
import sys
import socket
import json
import tablero
import threading as th

from config import (
    BLACK,
    WHITE,
    ESPACIO,
    FILAS,
    ANCHO,
    ALTO,
    TAMAÑO_CUADROS,
    BUFFER_SIZE,
    IP,
    PORT,
)

# Configuración de la conexión al servidor
SERVER_ADDRESS = (IP, PORT)

SCREEEN = tablero.inicializar_screen()

def sendMessage(ClientSocket, action ,bot = None, position=[], ships = {}):
    responseData = {
        "action": action,
        "bot": bot,
        "ships":ships,
        "position": position
    }
    ClientSocket.sendto(json.dumps(responseData).encode(), SERVER_ADDRESS)

def recvMessage(ClientSocket, timeout = 5):
    ClientSocket.settimeout(timeout)
    # try: 
    response, _ = ClientSocket.recvfrom(BUFFER_SIZE)
    response_data = json.loads(response.decode())
    print("respuesta:", response_data)
    # except:
        # response_data = {}
    return response_data 

def recvMessageTh(ClientSocket):
    print("Thread working")
    ClientSocket.settimeout(2)
    # try: 
    response, _ = ClientSocket.recvfrom(BUFFER_SIZE)
    response_data = json.loads(response.decode())
    print("respuesta:", response_data)
    # except:
        # response_data = {}
    print("Cerrando thread")

def disconnect(ClientSocket):
    sendMessage(ClientSocket, action="d")
    
    # Lógica para desconectar la sesión de juego
    print("Sesión cerrada...")
    ClientSocket.close()
    # enviar json al servidor para la desconexion

    pygame.quit()
    sys.exit()

def main_menu():
    font = pygame.font.Font(None, 36)
    singleplayer_text = font.render("Un jugador", True, WHITE)
    multiplayer_text = font.render("Modo multijugador", True, WHITE)
    singleplayer_rect = singleplayer_text.get_rect(center=(ANCHO // 2, ALTO // 2 - 50))
    multiplayer_rect = multiplayer_text.get_rect(center=(ANCHO // 2, ALTO // 2 + 50))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if singleplayer_rect.collidepoint(x, y):
                    return "singleplayer"  # El jugador eligió jugar contra un jugador
                elif multiplayer_rect.collidepoint(x, y):
                    return "multiplayer"  # El jugador eligió el modo multijugador

        SCREEEN.fill(BLACK)
        SCREEEN.blit(singleplayer_text, singleplayer_rect)
        SCREEEN.blit(multiplayer_text, multiplayer_rect)
        pygame.display.flip()


def connect(client_socket, msg, action = "c", bot = 0):
    # Mostrar pantalla de conexión
    connecting = True
    font = pygame.font.Font(None, 36)
    text = font.render(msg, True, WHITE)

    text_rect = text.get_rect(center=(ANCHO // 2, ALTO // 2))
    screen = tablero.inicializar_screen()

    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()
    while connecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        sendMessage(client_socket, action)
        # client_socket.sendto(json.dumps({"action": "c"}).encode(), SERVER_ADDRESS)
        try:
            client_socket.settimeout(2)
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            response_data = json.loads(response.decode())
            print("respuesta: ", response_data)
            if response_data["status"] == 1:
                connecting = False  # Termina la fase de conexión
                # response_data
        except socket.error as e:
            connecting = True
            print("Error", e)

def waitingTurn(client_socket, msg= "Esperando turno"):
        # Mostrar pantalla de conexión
    connecting = True
    while connecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        client_socket.settimeout(2)
        # client_socket.sendto(json.dumps({"action": "c"}).encode(), SERVER_ADDRESS)
        try:
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            response_data = json.loads(response.decode())
            print("respuesta: ", response_data)
            if response_data["status"] == 1:
                connecting = False  # Termina la fase de conexión
                # response_data
        except socket.error as e:
            connecting = True
            print("Error", e)
            print("Esperando turno")
    return True

def start_game(client_socket, ships):
    # Posicionar barcos en tablero, enviar json al servidor
    sendMessage(client_socket, "b", ships = ships)
    recvMessage(client_socket)
    print("Inicio el juego...")
    
def createButton(posicion, texto):
        button = pygame.Rect(posicion, 600, 200, 50)
        pygame.draw.rect(SCREEEN, BLACK, button)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(texto, True, WHITE)
        text_rect = text_surface.get_rect(center=button.center)
        SCREEEN.blit(text_surface, text_rect)

def puttingShips(client_socket):
    puttingShips = True
    ships = tablero.randomBoardSets()
    while puttingShips:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x < (50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)) and 50 <= y < (
                    50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)
                ):
                    # El clic está dentro del tablero
                    fila = (y - 50) // (TAMAÑO_CUADROS + ESPACIO)
                    columna = (x - 50) // (TAMAÑO_CUADROS + ESPACIO)
                    # casilla = (fila, columna)
         

                if (ANCHO // 2) - 200 <= x <= (ANCHO // 2) - 10 and 600 <= y <= 650:
                    # Verificar si se hizo clic en el botón "Desconectar"
                    disconnect(client_socket)  
                elif (ANCHO // 2) + 10 <= x <= (ANCHO // 2) + 200 and 600 <= y <= 650:
                    start_game(client_socket, ships)  # Verificar si se hizo clic en el botón "Iniciar Partida"
                    puttingShips = False
                elif (( ANCHO // 2) + 230 <= x <= (ANCHO // 2) + 230 + 200 and 600 <= y <= 650):
                    ships = tablero.randomBoardSets()
                    print("Tablero random generado!")


        SCREEEN.fill(WHITE)
        tablero.draw_board_with_ships(SCREEEN, "Selecciona la posicion de tus barcos", 0, 0)
        # tablero.draw_board_with_title(SCREEEN, "Tablero Enemigo", 600, 0)
        disconnect_button_x = ANCHO // 2 - (420) // 2
        start_game_button_x = disconnect_button_x + 220
        random_ships = start_game_button_x + 220
        createButton(disconnect_button_x, "Desconectar")
        createButton(start_game_button_x, "Iniciar Partida")
        createButton(random_ships, "Random")
        pygame.display.flip()

def main():
    # Inicializar la conexión al servidor
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connect(client_socket, "Conectando al servidor...") ## Inicia conexion al servidor

    unselected = True
    ## Main menu
    while unselected:
        selected_mode = main_menu()
        if selected_mode == "singleplayer":
            sendMessage(client_socket, action="s", bot = 1)
            recvMessage(client_socket)
            # Iniciar el juego en modo un jugador
            print("Modo de un jugador seleccionado")
            # Llama a la función start_game() para comenzar el juego en modo un jugador
            unselected = False
        elif selected_mode == "multiplayer":
            unselected = False
            connect(client_socket,"Esperando jugador..." , action="s")
            # sendMessage(client_socket, action="s", bot = 0)
            # client_socket.settimeout(100)
            # response, _ = client_socket.recvfrom(BUFFER_SIZE)
            # response_data = json.loads(response.decode())
            # print("respuesta:", response_data)
            # start_game(client_socket)
            # Iniciar el juego en modo multijugador
            print("Modo multijugador seleccionado")
            # Agrega aquí la lógica para iniciar el juego en modo multijugador
    # puttingShips = True
    puttingShips(client_socket)
    msg = recvMessage(client_socket)
    while True:
        myturn = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x < (50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)) and 50 <= y < (
                    50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)
                ) and myturn:
                    # El clic esta en mi tablero
                    fila = (y - 50) // (TAMAÑO_CUADROS + ESPACIO)
                    columna = (x - 50) // (TAMAÑO_CUADROS + ESPACIO)
                    casilla = (fila, columna)
                    # tablero.casillas_clickeadas.add(casilla)
                    # sendMessage(client_socket, action="a", position=[fila, columna])
                    print("No es clickeable")
                    print(fila, columna)
                if 50 + 600 <= x < 600 + (50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)) and 50 <= y < (
                    50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)
                ) and myturn:
                    # El clic está dentro del tablero enemigo
                    fila = (y - 50) // (TAMAÑO_CUADROS + ESPACIO)
                    columna = (x - 50 - 600) // ((TAMAÑO_CUADROS + ESPACIO))
                    casilla = (fila, columna)
                    tablero.casillas_clickeadas.add(casilla)
                    sendMessage(client_socket, action= "a", position=[fila, columna])
                    msg = recvMessage(client_socket)
                    if(msg["action"] == "a" and msg["status"] == 1):
                        tablero.barcos_enemigo.add(casilla)
                    msg = recvMessage(client_socket)
                    if(msg["action"] == "a" and msg["position"] != None):
                        tablero.click_enemigo.add((msg["position"][0], msg["position"][1]))
                        if(msg["status"] == 1):
                            print("Impacto en nuestro barco!")
                        # print(tablero.click_enemigo)
                    print(fila, columna)

                if (ANCHO // 2) - 200 <= x <= (ANCHO // 2) - 10 and 600 <= y <= 650:
                    disconnect(
                        client_socket
                    )  # Verificar si se hizo clic en el botón "Desconectar"
                elif (ANCHO // 2) + 10 <= x <= (ANCHO // 2) + 200 and 600 <= y <= 650:
                    pass
                    # start_game(client_socket)  # Verificar si se hizo clic en el botón "Iniciar Partida"

        SCREEEN.fill(WHITE)
        tablero.draw_board_with_title(SCREEEN, "Tablero Jugador", 0, 0)
        tablero.draw_board_with_title_enemy(SCREEEN, "Tablero Enemigo", 600, 0)
        disconnect_button_x = ANCHO // 2 - (420) // 2
        start_game_button_x = disconnect_button_x + 220
        createButton(disconnect_button_x, "Desconectar")
        createButton(start_game_button_x, "Iniciar Partida")
        pygame.display.flip()

if __name__ == "__main__":
    main()
