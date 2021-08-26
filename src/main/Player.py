class Player:

    def __init__(self, color, name, board=None):
        self.board = None
        self.king = None
        self.pieces = []
        self.color = color
        self.name = name
        self.selected = None
        self.eaten = []

    def get_eaten_string(self):
        txt = ""
        for p in self.eaten:
            txt += str(p)
        return txt

    @property
    def eaten_value(self):
        val = 0
        for p in self.eaten:
            val += p.value
        return val

    def is_check(self):
        return self.board.is_check(self)

    def is_checkmate(self):
        return self.board.is_checkmate(self)

    def can_move(self):
        for piece in self.pieces:
            if len(piece.get_possible_moves()) != 0:
                return True
        return False

    def possible_moves(self):
        poss = {}
        for piece in self.pieces:
            poss[piece] = piece.get_possible_moves()

        return poss
