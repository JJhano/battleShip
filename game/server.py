import socket
import json
from clases.GameSession import GameSession
import random as r
from config import BUFFER_SIZE, IP, PORT, SIZE


PLAYERS = []
SESSIONS = []
SESSION_COUNT = 0


def printMatrix(matrix):
    for row in matrix:
        print(" ".join(map(str, row)))

def foundSession(ip):
    for session in SESSIONS:
        if ip == session.player1.ip[0]:
            return session.sessionId, session.player1.board, session
        elif ip == session.player2.ip[0]:
            return session.sessionId, session.player2.board, session

def endGame(UDPServerSocket, ipPlayerLost, ipPlayerWin, bot = False):
    sendMessage(UDPServerSocket, ipPlayerLost, "l", 1)
    sendMessage(UDPServerSocket, ipPlayerWin, "w", 1)

def sendMessage(UDPServerSocket, address, action ,status,position=None):
    responseData = {
        "action": action,
        "status": status,
        "position": position
    }
    print("Mensaje enviado: ", responseData)
    UDPServerSocket.sendto(json.dumps(responseData).encode(), address)

    

def selectionMode(UDPServerSocket, received_data, address):
    global SESSION_COUNT
    PLAYERS.append(address)
    selectModeGame = received_data["bot"]
    if selectModeGame == 1:
        gameSession = GameSession(SESSION_COUNT, address, ("1","1"),1)
        SESSION_COUNT +=1
        SESSIONS.append(gameSession)
        print("Empieza partida contra bot")
        gameSession.player2.randomBoard()
        printMatrix(gameSession.player2.board)
        sendMessage(UDPServerSocket,address, "s",1)
        PLAYERS.remove(address)
    else:
        # Implementa la lógica para esperar a otro jugador.
        if len(PLAYERS) % 2 == 0:
            gameSession = GameSession(SESSION_COUNT, PLAYERS[0], PLAYERS[1],0)
            SESSION_COUNT += 1
            SESSIONS.append(gameSession)
            print("SESION", gameSession.sessionId, "\nJugador 1:", gameSession.player1.ip, "vs", "Jugador 2:", gameSession.player2.ip)
            sendMessage(UDPServerSocket, PLAYERS[0],"s",1)
            sendMessage(UDPServerSocket, PLAYERS[1],"s",1)
            PLAYERS.clear()
        # else:
        #     sendMessage(UDPServerSocket, PLAYERS[0],"s",2)

def takeAction(UDPServerSocket):
    global SESSION_COUNT
    bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    received_data = json.loads(message.decode())
    print(received_data)
    action = received_data["action"]
    print(SESSIONS)
    if action == "c":
        sendMessage(UDPServerSocket, address,"c",1)
    elif action == "s":
        selectionMode(UDPServerSocket, received_data, address)

    elif action == "a":
        idSession, boardFounded, session = foundSession(address[0])
        x, y = received_data["position"]   
        if (session.bot == 1): #Bot
            if(SESSIONS[idSession].player1.ip == address):
                hit = SESSIONS[idSession].player2.attackBoard(x, y)
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip,"a", hit)
                print("Generando ataque bot...")
                ##Ataque del bot
                x_bot, y_bot = SESSIONS[idSession].player1.botAtack(r.randint(0, SIZE - 1), r.randint(0, SIZE - 1))
                print(x_bot, y_bot)
                hit = 0
                if SESSIONS[idSession].player1.board[x][y] == 2:
                    hit = 1
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip,"a",hit, [x_bot, y_bot])
        else:
            if SESSIONS[idSession].player1.ip == address:
                hit = SESSIONS[idSession].player2.attackBoard(x, y)
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip,"a",hit)
                sendMessage(UDPServerSocket, SESSIONS[idSession].player2.ip, "a",hit,[x,y])
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip, "t",0)
                sendMessage(UDPServerSocket, SESSIONS[idSession].player2.ip, "t",1)
            else:
                hit = SESSIONS[idSession].player1.attackBoard(x, y)
    
                sendMessage(UDPServerSocket, SESSIONS[idSession].player2.ip,"a",hit)
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip, "a",hit,[x,y])
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip, "t",1)
                sendMessage(UDPServerSocket, SESSIONS[idSession].player2.ip, "t",0)

            if SESSIONS[idSession].player1.lost() and not session.bot:
                endGame(UDPServerSocket, SESSIONS[idSession].player1.ip, SESSIONS[idSession].player2.ip)

            elif SESSIONS[idSession].player2.lost() and not session.bot:
                endGame(UDPServerSocket, SESSIONS[idSession].player2.ip, SESSIONS[idSession].player1.ip)
            elif SESSIONS[idSession].player1.lost() and session.bot:
                sendMessage(UDPServerSocket, address, "l", 1)
            elif SESSIONS[idSession].player2.lost() and session.bot:
                sendMessage(UDPServerSocket, address, "w", 1)
    elif action == "b":
        idSession, boardFounded, session = foundSession(address[0])
        ships = received_data["ships"]
        print(ships)
        for i in ships:
            if i == "p":
                boardFounded[ships[i][0]][ships[i][1]] = 1
            elif i == "b":        
                if ships[i][2] == 0:
                    print(ships[i][0], ships[i][1])
                    print(ships[i][0] + 1, ships[i][1])
                    boardFounded[ships[i][0]][ships[i][1]] = 1
                    boardFounded[ships[i][0] + 1][ships[i][1]] = 1
                else:
                    boardFounded[ships[i][0]][ships[i][1]] = 1
                    boardFounded[ships[i][0]][ships[i][1] + 1] = 1
            elif i == "s":
                if ships[i][2] == 0:
                    boardFounded[ships[i][0]][ships[i][1]] = 1
                    boardFounded[ships[i][0] + 1][ships[i][1]] = 1
                    boardFounded[ships[i][0] + 2][ships[i][1]] = 1
                else:
                    boardFounded[ships[i][0]][ships[i][1]] = 1
                    boardFounded[ships[i][0]][ships[i][1] + 1] = 1
                    boardFounded[ships[i][0]][ships[i][1] + 2] = 1
        if SESSIONS[idSession].player1.ip == address:
            SESSIONS[idSession].player1.board = boardFounded
            sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip, "b",1)
            SESSIONS[idSession].player1.start = True
            if session.bot == 1:
                sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip, "t",1)
                # SESSIONS[idSession].player2.start = True
        elif(not session.bot):
            SESSIONS[idSession].player2.board = boardFounded
            sendMessage(UDPServerSocket, SESSIONS[idSession].player2.ip, "b", 1)
            SESSIONS[idSession].player2.start = True
        
        if (SESSIONS[idSession].player1.start and SESSIONS[idSession].player2.start):
            sendMessage(UDPServerSocket, SESSIONS[idSession].player1.ip, "t",1)
            sendMessage(UDPServerSocket, SESSIONS[idSession].player2.ip, "t",0)
 
        
    elif action == "d":
        idSession, boardFounded, session = foundSession(address[0])
        if(session.player1.ip == address and not session.bot):
            # endGame(UDPServerSocket, session.player1, session.player2)
            sendMessage(UDPServerSocket, session.player1.ip, "d", 1)
            sendMessage(UDPServerSocket, session.player2.ip, "w", 1)
        elif (not session.bot):
            # endGame(UDPServerSocket, session.player2, session.player1)
            sendMessage(UDPServerSocket, session.player2.ip, "d", 1)
            sendMessage(UDPServerSocket, session.player1.ip, "w", 1)
        else:
            sendMessage(UDPServerSocket, session.player1.ip, "d", 1)
  
        SESSIONS.remove(SESSIONS[idSession])



def main():
    msgFromServer = "Hello UDP Client"
    # bytesToSend = str.encode(msgFromServer)

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((IP, PORT))
    print("UDP server up and listening")

    while True:
        takeAction(UDPServerSocket)

        # Implementa el temporizador de 10 segundos para desconectar al jugador si no juega.

        # UDPServerSocket.sendto(bytesToSend, address)


if __name__ == "__main__":
    main()