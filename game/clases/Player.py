from config import SIZE
import random as r

class Player:
    def __init__(self, ip):
        self.ip = ip
        # print("PlayerIp: ", self.ip)
        self.board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        self.start = False

    def changeBoard(self, x, y):
        if self.board[x][y] == 0:
            self.board[x][y] = 1

    def attackBoard(self, x, y):
        # if sessions[idSession].player1.ip == adress[0]:
        if self.board[x][y] == 1: # Casilla con barco
            self.board[x][y] = 2 # Casilla con barco impactado
            return 1
        else: 
            self.board[x][y] = 3
        return 0

    def botAtack(self, x ,y):
        while(self.board[x][y] == 3 or self.board[x][y] == 2):            
            x = r.randint(0, SIZE - 1)
            y = r.randint(0, SIZE - 1)
        self.attackBoard(x, y)
        # print("ataque bot: ", x, y)
        return x, y
        
    def lost(self):
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] == 1:
                    return False
        return True

    def randomBoard(self):
        for tamano in [1, 2, 3]:
            while True:
                fila = r.randint(0, SIZE - 1)
                columna = r.randint(0, SIZE - 1)
                while(fila > SIZE + tamano):
                    fila = r.randint(0, SIZE - 1)
                while(columna > SIZE + tamano):
                    columna = r.randint(0, SIZE - 1)
                direccion = r.choice(['horizontal', 'vertical'])

                if direccion == 'horizontal':
                    if (columna + tamano - 1) >= SIZE:
                        continue
                    ocupado = False
                    for c in range(columna, columna + tamano):
                        if self.board[fila][c] == 1:
                            ocupado = True
                            break
                    if ocupado:
                        continue
                    for c in range(columna, columna + tamano):
                        self.board[fila][c] = 1
                    break
                else:
                    if (fila + tamano - 1) >= SIZE:
                        continue
                    ocupado = False
                    for f in range(fila, fila + tamano):
                        if self.board[f][columna] == 1:
                            ocupado = True
                            break
                    if ocupado:
                        continue
                    for f in range(fila, fila + tamano):
                        self.board[f][columna] = 1
                    break