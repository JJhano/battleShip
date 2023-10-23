from clases.Player import Player


class GameSession:
    def __init__(self, sessionId, ip1, ip2, bot):
        self.sessionId = sessionId
        self.player1 = Player(ip1)
        self.player2 = Player(ip2)
        self.Turn = True # Turno 1 = player 1 jugando
        self.bot = bot
