import pygame
import sys
import socket
import json
import tablero
import threading as th
import time

from config import ( BLACK, WHITE, ESPACIO, FILAS, ANCHO, ALTO,
    TAMAÑO_CUADROS, BUFFER_SIZE, IP, PORT,)

# Configuración de la conexión al servidor
SERVER_ADDRESS = (IP, PORT)
ACTIONS = []
SCREEEN = tablero.inicializar_screen()
myturn = True
gameover = False
win = False
# waitingPlayer = True
multiplayer = False

def sendMessage(ClientSocket, action ,bot = None, position=[], ships = {}):
    responseData = {
        "action": action,
        "bot": bot,
        "ships":ships,
        "position": position
    }
    print("MENSAJE ENVIADO", responseData)
    ClientSocket.sendto(json.dumps(responseData).encode(), SERVER_ADDRESS)

def recvMessage(ClientSocket, timeout = 2):
    try: 
        ClientSocket.settimeout(timeout)
        response, _ = ClientSocket.recvfrom(BUFFER_SIZE)
        response_data = json.loads(response.decode())
        print("respuesta:", response_data)
        return response_data
    except:
        pass

def waitThreadAction():
    while (len(ACTIONS) == 0):
        time.sleep(0.5)

def disconnect(client_socket):
    sendMessage(client_socket, action="d")
    # Lógica para desconectar la sesión de juego
    print("Sesión cerrada...")
    client_socket.close()
    # enviar json al servidor para la desconexion
    pygame.quit()
    sys.exit()
#No tocar
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


def gameOver(client_socket, msg, thread):
    
    # Mostrar pantalla de conexión
    font = pygame.font.Font(None, 36)
    text = font.render(msg, True, WHITE)

    text_rect = text.get_rect(center=(ANCHO // 2, ALTO // 2))
    screen = tablero.inicializar_screen()

    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()
    thread.join()
    time.sleep(2)
    pygame.quit()
    disconnect(client_socket)
    sys.exit()

def showText(msg, x, y):
    font = pygame.font.Font(None, 36)
    text = font.render(msg, True, WHITE)
    text_rect = text.get_rect(center=(x, y))
    screen = tablero.inicializar_screen()
    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()
#No tocar
def connecting(client_socket, msg, action = "c", bot = 0): #No tocar
    # Mostrar pantalla de conexión
    connecting = True
    showText(msg, ANCHO //2, ALTO //2)
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

#No tocar
def waitingPlayer(client_socket, msg):
    # Mostrar pantalla de conexión
    connecting = True
    showText(msg, ANCHO //2, ALTO //2)
    while connecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # sendMessage(client_socket, action)
        # client_socket.sendto(json.dumps({"action": "c"}).encode(), SERVER_ADDRESS)
        try:
            print("ACTIONS:\n",ACTIONS)
            waitThreadAction()
            msg = ACTIONS[0]
            print("Eliminado?")
            ACTIONS.remove(ACTIONS[0])
            print("ACTIONS:\n",ACTIONS)
            if(msg["action"] == "s" and msg["status"] == 1):
                connecting = False

        except socket.error as e:
            connecting = True
            # print("Error", e)

def createButton(posicion, texto):
        button = pygame.Rect(posicion, 600, 200, 50)
        pygame.draw.rect(SCREEEN, BLACK, button)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(texto, True, WHITE)
        text_rect = text_surface.get_rect(center=button.center)
        SCREEEN.blit(text_surface, text_rect)

def puttingShips(client_socket):
    puttingShips = True
    send = False
    ships = tablero.randomBoardSets()
    while puttingShips:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                disconnect(client_socket)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x < (50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)) and 50 <= y < (
                    50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)
                ):
                    pass

                if (ANCHO // 2) - 200 <= x <= (ANCHO // 2) - 10 and 600 <= y <= 650:
                    # Verificar si se hizo clic en el botón "Desconectar"
                    disconnect(client_socket)  
                elif (ANCHO // 2) + 10 <= x <= (ANCHO // 2) + 200 and 600 <= y <= 650 and not send:
                      # Verificar si se hizo clic en el botón "Iniciar Partida"
                    puttingShips = False
                    send = True
                    sendMessage(client_socket, "b", ships = ships)
                    msg = takeAction(client_socket)
         
                elif (( ANCHO // 2) + 230 <= x <= (ANCHO // 2) + 230 + 200 and 600 <= y <= 650) and not send:
                    ships = tablero.randomBoardSets()
                    print("Tablero random generado!")


        SCREEEN.fill(WHITE)
        tablero.draw_board_with_ships(SCREEEN, "Posiciona tus barcos", 0, 0)
        # tablero.draw_board_with_title(SCREEEN, "Tablero Enemigo", 600, 0)
        disconnect_button_x = ANCHO // 2 - (420) // 2
        start_game_button_x = disconnect_button_x + 220
        random_ships = start_game_button_x + 220
        createButton(disconnect_button_x, "Desconectar")
        createButton(start_game_button_x, "Iniciar Partida")
        createButton(random_ships, "Random")
        #Texto
        # if(waitingPlayer):      
        #     font = pygame.font.Font(None, 36) 
        #     text = font.render("Esperando jugador...", True, BLACK)
        #     text_rect = text.get_rect()
        #     text_rect.centerx = SCREEEN.get_rect().centerx
        #     text_rect.bottom = ALTO - 120
        #     SCREEEN.blit(text, text_rect)
        pygame.display.flip()

def takeAction(client_socket):
    global gameover, myturn, win
    msg = recvMessage(client_socket, 1)
    if msg != None:
        if(msg["action"] == "a" and msg["position"] != [] ):
            tablero.click_enemigo.add((msg["position"][0], msg["position"][1]))
            if(msg["status"] == 1):
                print("Impacto en nuestro barco!")
        elif msg["action"] == "t" and msg["status"] == 1:
            myturn = True
        elif msg["action"] == "t" and msg["status"] == 0:
            myturn = False
        elif msg["action"] == "l" and msg["status"] == 1 or msg["action"] == "d":
            gameover = True
        elif(msg["action"] == "w"):
            gameover = True
            win = True
    return msg

#Thread 1 funcion que se ejecuta en el thread
def takeMessages(client_socket):
    global gameover, myturn, win, ACTIONS
    print("Th working")
    while True:
        try:
            msg = recvMessage(client_socket, 2)
            if msg != None:
                if msg["action"] == "t":
                    if(msg["status"] == 1):
                        print("Its my turn")
                        # ACTIONS.remove(msg)
                        myturn = True
                    else:
                        print("It isnt my turn")
                        # ACTIONS.remove(msg)
                        myturn = False
                # elif(msg["action"] == "a" and msg["position"] != []):
                elif(msg["action"] == "a" and msg["position"] != [] and not myturn):
                    tablero.click_enemigo.add((msg["position"][0], msg["position"][1]))
                    if(msg["status"] == 1):
                        # tablero.barcos_enemigos.add((msg["status"][0], msg["status"][1]))
                        print("Impacto en nuestro barco!")
                    # ACTIONS.remove(msg)
                elif msg["action"] == "l"  or msg["action"] == "d":
                    gameover = True
                elif(msg["action"] == "w"):
                    gameover = True
                    win = True
                elif(msg["action"] != "b"):
                        ACTIONS.append(msg)
                # print("Mensajes recibidos =", len(ACTIONS))
                # print("ACTIONS:\n",ACTIONS)

        except NameError as e:
            print("FAIL TH2", e)
        # return msg
#             print("FAIL TH2", e)

def main():
    global ACTIONS, multiplayer, gameover, myturn, win
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ## Inicia conexion al servidor
    connecting(client_socket, "Conectando al servidor...") 
    thread = th.Thread(target = takeMessages, args = (client_socket,), daemon = True)
    thread.start()
    
    while True:
        unselected = True
        ## Main menu select mode
        while unselected:
            selected_mode = main_menu()
            if selected_mode == "singleplayer":
                sendMessage(client_socket, action="s", bot = 1)
                print("ACTIONS:\n",ACTIONS)
                while len(ACTIONS) == 0:
                    time.sleep(0.5)
                msg = ACTIONS[0]
                print("Eliminado?")
                ACTIONS.remove(ACTIONS[0])
                print("ACTIONS:\n",ACTIONS)
                if(msg["action"] == "s" and msg["status"] == 1):
                    unselected = False
                # Iniciar el juego en modo un jugador
                print("Modo de un jugador seleccionado")
                # Llama a la función start_game() para comenzar el juego en modo un jugador
                unselected = False
            elif selected_mode == "multiplayer":
                sendMessage(client_socket, action="s", bot = 0)
                multiplayer = True
                unselected = False
                print("Modo multijugador seleccionado")
                # Agrega aquí la lógica para iniciar el juego en modo multijugador

        if(multiplayer):
            waitingPlayer(client_socket, "Esperando jugador...")
        #Putting ships
        puttingShips(client_socket)
        # myturn = False
        cont = 0
        while not gameover:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    disconnect(client_socket)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 50 <= x < (50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)) and 50 <= y < (
                        50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)
                    ) and myturn:
                        pass
                    elif (50 + 600 <= x < 600 + (50 + FILAS * (TAMAÑO_CUADROS + ESPACIO))) and (50 <= y < (
                        50 + FILAS * (TAMAÑO_CUADROS + ESPACIO)
                    )) and myturn:
                        # El clic está dentro del tablero enemigo
                        fila = (y - 50) // (TAMAÑO_CUADROS + ESPACIO)
                        columna = (x - 50 - 600) // ((TAMAÑO_CUADROS + ESPACIO))
                        casilla = (fila, columna)
                        if(casilla not in tablero.casillas_clickeadas):
                            sendMessage(client_socket, action= "a", position=[fila, columna])
                            waitThreadAction()
                            msg = ACTIONS[0]
                            print("msg if ACTION[0]", msg)
                            ACTIONS.remove(ACTIONS[0])
                            # msg = takeAction(client_socket)
                            # if msg["action"] == "a" and msg["status"] == 1 and msg["position"] == []: #real
                            if msg["action"] == "a" and msg["status"] == 1:
                                print("---------------------------------")
                                print("MSGIF: msg", msg)
                                print("Impacto tablero enemigo")
                                print("CASILLA", casilla)
                                tablero.barcos_enemigo.add(casilla)
                                tablero.casillas_clickeadas.add(casilla)
                            else:
                                tablero.casillas_clickeadas.add(casilla)
                        print(fila, columna)
                    elif (ANCHO // 2) - 200 <= x <= (ANCHO // 2) - 10 and 600 <= y <= 650:
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
            #Texto
            font = pygame.font.Font(None, 36)     
            if(myturn):      
                text = font.render("Es tu turno", True, BLACK)
            else:
                text = font.render("Esperando Ataque enemigo", True, BLACK)
            text_rect = text.get_rect()
            text_rect.centerx = SCREEEN.get_rect().centerx
            text_rect.bottom = ALTO - 120
            SCREEEN.blit(text, text_rect)
             
            pygame.display.flip()

            cont += 1
        if win:
            gameOver(client_socket, "Ganaste", thread)
            # thread.join()

        else:
            gameOver(client_socket, "Perdiste", thread)
            # thread.join()

if __name__ == "__main__":
    main()
