import abc
import types
from pychess.player import COLOR_BLACK, COLOR_WHITE
import pychess.signals as signals


class Piece:

    SAN_LETTER = "?"

    def __init__(self, player, value, row=None, col=None, board=None):
        self.player = player
        self.color = player.color
        self.row = row  # The rank of the piece
        self.col = col  # The file of the piece
        self.board = board
        self.value = value
        player.pieces.append(self)

    def display(self):
        return self.icon()

    @abc.abstractmethod
    def can_move(self, row, col, ignoreillegal=False):
        pass

    def move(self, row, col, check=True):
        if not check or self.can_move(row, col):
            signals.PIECE_MOVE.send(self, start=(self.row, self.col), dest=(row, col))
            self.board.ranks[self.row][self.col] = None

            # If there is a piece where we move, we eat it
            if self.board.ranks[row][col] is not None:
                self.board.ranks[row][col].on_eat(self)

            self.board.ranks[row][col] = self
            self.row = row
            self.col = col

            return True

        return False

    @abc.abstractmethod
    def get_possible_moves(self):
        pass

    def on_eat(self, piece):
        signals.PIECE_TAKEN.send(self, attacker=piece)
        self.row = None
        self.col = None
        piece.player.eaten.append(self)

    def __str__(self):
        return str(self.icon()) + " at x=" + str(self.row) + " y=" + str(self.col)

    def icon(self):
        return "?"

    @property
    def san(self):
        if self.color == COLOR_WHITE:
            return self.SAN_LETTER.upper()
        else:
            return self.SAN_LETTER.lower()


class Pawn(Piece):

    SAN_LETTER = "P"
    VALUE = 1

    def __init__(self, player, row=None, col=None):
        # Forward direction for the pawn, 1 if white, -1 if black
        self.direction = 1 if player.color == 0 else -1
        self.has_moved = False
        super().__init__(player, self.VALUE, row, col)

    def icon(self):
        if self.color == 0:
            return "♙"
        else:
            return "♟"

    def can_move(self, row, col, ignoreillegal=False):

        # The piece is not on the board
        if self.row is None or self.col is None or self.board is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(row, col):
            return False

        # The cell is two cells in front of the pawn and has not moved
        if row == self.row + 2 * self.direction and col == self.col and self.has_moved == False:
            # If one of the two cells in front of him is occupied
            if self.board.get_cell(row - self.direction, col) is not None or self.board.get_cell(row, col) is not None:
                return False
            else:
                # The cells are free, we check if the pawn is in the first two ranks on his side
                if self.direction == 1 and self.row > 1:  # White pawn
                    return False

                if self.direction == -1 and self.row < 6:  # Black pawn
                    return False

        # The cell is not in the forward direction
        elif row != self.row + self.direction:
            return False

        # The cell in front of the pawn is occupied
        if col == self.col:
            if self.board.get_cell(row, col) is not None:
                return False

        elif col == self.col + 1 or col == self.col - 1:
            # Here, the cell is a diagonal, so there must be a piece in order to move here
            # If the cell is empty or the piece is owned by the same player, we cannot move here
            piece = self.board.get_cell(row, col)
            if piece is None:
                # The cell is empty, we check if we can en passant
                if self.board.en_passant is not None and (row, col) == self.board.en_passant:
                    # We can en passant
                    pass
                else:
                    # We cannot move here
                    return False
            elif self.player == piece.player:
                return False

        else:
            # The cell is not in diagonal or in front of the pawn
            return False

        # Now, we check if the move is illegal
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.row, self.col, row, col)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.row is None or self.col is None:
            return []

        # Every cell where the pawn could move
        allowed = [(self.row + self.direction, self.col + i) for i in range(-1, 2)]
        if not self.has_moved and (self.row == 1 or self.row == self.board.shape[0] - 2):
            allowed.append((self.row + 2 * self.direction, self.col))

        # Check if they can move in the possible cells
        possible = []
        for c in allowed:
            if self.can_move(c[0], c[1]):
                possible.append(c)
        return possible

    def move(self, row, col, check=True):
        if self.can_move(row, col):

            # We check if we take en passant
            en_passant = False
            if self.board.en_passant is not None:
                ep_row, ep_col = self.board.en_passant
                if row == ep_row and col == ep_col:
                    en_passant = True

            super().move(row, col, check=False)
            self.has_moved = True

            if en_passant:
                # Eat the opponent's pawn
                self.board.get_cell(row - self.direction, col).on_eat(self)
                self.board.ranks[row - self.direction][col] = None

            # We check if the pawn can promote
            if row == 0 or row == self.board.shape[0] - 1:
                signals.PAWN_PROMOTION.send(self)

    def promote(self, piece_type):
        # Override instance methods to the ones of the piece promoted to
        self.icon = types.MethodType(piece_type.icon, self)
        self.display = types.MethodType(piece_type.display, self)
        self.can_move = types.MethodType(piece_type.can_move, self)
        self.get_possible_moves = types.MethodType(piece_type.get_possible_moves, self)
        self.move = types.MethodType(piece_type.move, self)
        self.value = piece_type.VALUE
        signals.PAWN_PROMOTED.send(self, piece_type=piece_type)

    def on_eat(self, piece):
        self.icon = types.MethodType(Pawn.icon, self)
        self.display = types.MethodType(Pawn.display, self)
        self.value = 1
        super().on_eat(piece)


class Rook(Piece):

    SAN_LETTER = "R"
    VALUE = 5

    def __init__(self, player, row=None, col=None):
        self.has_moved = False
        super().__init__(player, self.VALUE, row, col)

    def move(self, row, col, check=True):
        if not check or super(Rook, self).move(row, col):
            self.has_moved = True

    def icon(self):
        if self.color == 0:
            return "♖"
        else:
            return "♜"

    def can_move(self, row, col, ignoreillegal=False):
        # The piece is not on the board
        if self.row is None or self.col is None or self.board is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(row, col):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(row, col)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if row == self.row and col == self.col:
            return False

        # Change column
        if row == self.row:
            # We check if the path is not blocked by another piece
            if col > self.col:
                direction = 1
            else:
                direction = -1

            for c in range(self.col + direction, col, direction):
                if self.board.get_cell(self.row, c) is not None:
                    return False
        # Change row
        elif col == self.col:
            # We check if the path is not blocked by another piece
            if row > self.row:
                direction = 1
            else:
                direction = -1

            for r in range(self.row + direction, row, direction):
                if self.board.get_cell(r, self.col) is not None:
                    return False
        else:
            return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.row, self.col, row, col)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.row is None or self.col is None:
            return []

        possible = []
        for col in (1, -1):
            i = 1
            while self.can_move(self.row + i * col, self.col):
                possible.append((self.row + i * col, self.col))
                i += 1

        for line in (1, -1):
            i = 1
            while self.can_move(self.row, self.col + i * line):
                possible.append((self.row, self.col + i * line))
                i += 1

        return possible


class Bishop(Piece):

    SAN_LETTER = "B"
    VALUE = 3

    def __init__(self, player, row=None, col=None):
        super().__init__(player, self.VALUE, row, col)

    def icon(self):
        if self.color == 0:
            return "♗"
        else:
            return "♝"

    def can_move(self, row, col, ignoreillegal=False):
        # The piece is not on the board
        if self.row is None or self.col is None or self.board is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(row, col):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(row, col)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if row == self.row and col == self.col:
            return False

        # The piece is not in a diagonal
        if row-col != self.row - self.col and row+col != self.row + self.col:
            return False

        # We check if the path is not blocked by another piece
        if col > self.col:
            coldir = 1
        else:
            coldir = -1

        if row > self.row:
            rowdir = 1
        else:
            rowdir = -1

        i = 1
        while self.row + i * rowdir != row and self.col + i * coldir != col:
            if self.board.get_cell(self.row + i * rowdir, self.col + i * coldir) is not None:
                return False
            i += 1

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.row, self.col, row, col)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.row is None or self.col is None:
            return []

        possible = []
        for xdir in (1, -1):
            for ydir in (1, -1):
                i = 1
                while self.can_move(self.row + i * xdir, self.col + i * ydir):
                    possible.append((self.row + i * xdir, self.col + i * ydir))
                    i += 1
        return possible


class Queen(Piece):

    SAN_LETTER = "Q"
    VALUE = 9

    def __init__(self, player, row=None, col=None):
        super().__init__(player, self.VALUE, row, col)

    def icon(self):
        if self.color == 0:
            return "♕"
        else:
            return "♛"

    def can_move(self, row, col, ignoreillegal=False):
        # The piece is not on the board
        if self.row is None or self.col is None or self.board is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(row, col):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(row, col)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if row == self.row and col == self.col:
            return False

        # The piece is in a diagonal
        if row - col == self.row - self.col or row + col == self.row + self.col:

            # We check if the path is not blocked by another piece
            if col > self.col:
                ydir = 1
            else:
                ydir = -1

            if row > self.row:
                xdir = 1
            else:
                xdir = -1

            i = 1
            while self.row + i * xdir != row and self.row + i * xdir != col:
                if self.board.get_cell(self.row + i * xdir, self.col + i * ydir) is not None:
                    return False
                i += 1

        # Column
        elif row == self.row:
            # We check if the path is not blocked by another piece
            if col > self.col:
                direction = 1
            else:
                direction = -1

            for line in range(self.col + direction, col, direction):
                if self.board.get_cell(self.row, line) is not None:
                    return False
        # Line
        elif col == self.col:
            # We check if the path is not blocked by another piece
            if row > self.row:
                direction = 1
            else:
                direction = -1

            for col in range(self.row + direction, row, direction):
                if self.board.get_cell(col, self.col) is not None:
                    return False

        else:
            return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.row, self.col, row, col)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.row is None or self.col is None:
            return []

        possible = []

        # Columns
        for col in (1, -1):
            i = 1
            while self.can_move(self.row + i * col, self.col):
                possible.append((self.row + i * col, self.col))
                i += 1

        # Lines
        for line in (1, -1):
            i = 1
            while self.can_move(self.row, self.col + i * line):
                possible.append((self.row, self.col + i * line))
                i += 1

        # Diagonals
        for xdir in (1, -1):
            for ydir in (1, -1):
                i = 1
                while self.can_move(self.row + i * xdir, self.col + i * ydir):
                    possible.append((self.row + i * xdir, self.col + i * ydir))
                    i += 1

        return possible


class Knight(Piece):

    SAN_LETTER = "N"
    VALUE = 3

    def __init__(self, player, row=None, col=None):
        super().__init__(player, self.VALUE, row, col)

    def icon(self):
        if self.color == 0:
            return "♘"
        else:
            return "♞"

    @property
    def _allowed_coordinates(self):
        return [
            (self.row + 1, self.col + 2), (self.row + 1, self.col - 2),
            (self.row - 1, self.col + 2), (self.row - 1, self.col - 2),
            (self.row + 2, self.col + 1), (self.row + 2, self.col - 1),
            (self.row - 2, self.col + 1), (self.row - 2, self.col - 1)
        ]

    def can_move(self, row, col, ignoreillegal=False):

        # The piece is not on the board
        if self.row is None or self.col is None or self.board is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(row, col):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(row, col)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if row == self.row and col == self.col:
            return False

        # The piece is not in an allowed place :
        if (row, col) not in self._allowed_coordinates:
            return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.row, self.col, row, col)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.row is None or self.col is None:
            return []

        possible = []
        for cell in self._allowed_coordinates:
            if self.can_move(cell[0], cell[1]):
                possible.append(cell)
        return possible


class King(Piece):

    SAN_LETTER = "K"
    VALUE = 0

    def __init__(self, player, row=None, col=None):
        player.king = self
        self.has_moved = False
        super().__init__(player, self.VALUE, row, col)

    def icon(self):
        if self.color == 0:
            return "♔"
        else:
            return "♚"

    def can_move(self, row, col, ignoreillegal=False):
        # The piece is not on the board
        if self.row is None or self.col is None or self.board is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(row, col):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(row, col)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if row == self.row and col == self.col:
            return False

        # The piece is not in an allowed place :
        if not ((self.row - 1 <= row <= self.row + 1) and (self.col - 1 <= col <= self.col + 1)):
            if not self.has_moved and row == self.row and col in (2, 6) and not self.board.is_check(self.player):
                # King side
                if col == 6:
                    p = self.board.get_cell(self.row, 7)
                    if isinstance(p, Rook) and p.player == self.player and not p.has_moved:
                        # We check if the path is blocked or attacked by another piece
                        if self.board.get_cell(self.row, 5) is not None or self.board.get_cell(self.row, 6) is not None:
                            # The path is blocked
                            return False

                        if self.board.is_illegal_move(self.player, self.row, self.col, self.row, 5):
                            # The path is attacked
                            return False
                    else:
                        return False

                # Queen side
                if col == 2:
                    p = self.board.get_cell(self.row, 0)
                    if isinstance(p, Rook) and p.player == self.player and not p.has_moved:
                        # We check if the path is blocked or attacked by another piece
                        if self.board.get_cell(self.row, 1) is not None or self.board.get_cell(self.row, 2) is not None or self.board.get_cell(self.row, 3) is not None:
                            # The path is blocked
                            return False

                        if self.board.is_illegal_move(self.player, self.row, self.col, self.row, 3):
                            # The path is attacked
                            return False
                    else:
                        return False

            else:
                return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.row, self.col, row, col)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.row is None or self.col is None:
            return []

        possible = []
        for x in range(self.row - 1, self.row + 2):
            for y in range(self.col - 1, self.col + 2):
                if self.can_move(x, y):
                    possible.append((x, y))

        if not self.has_moved:
            # Castling queen side
            if self.can_move(self.row, 2):
                possible.append((self.row, 2))
            # Castling king side
            if self.can_move(self.row, 6):
                possible.append((self.row, 6))
        return possible

    def move(self, row, col, check=True):
        if not check or super().move(row, col):
            if not self.has_moved and col in (2, 6):
                # Castling
                if col == 2:
                    # Queen side
                    # Move the rook
                    rook, self.board.ranks[self.row][0] = self.board.ranks[self.row][0], None
                    self.board.ranks[self.row][3] = rook
                    rook.col = 3

                if col == 6:
                    # King side
                    # Move the rook
                    rook, self.board.ranks[self.row][7] = self.board.ranks[self.row][7], None
                    self.board.ranks[self.row][5] = rook
                    rook.col = 5

            self.has_moved = True
