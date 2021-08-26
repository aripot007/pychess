import abc
import types


class Piece:

    def __init__(self, player, value, x=None, y=None, board=None):
        self.player = player
        self.color = player.color
        self.x = x
        self.y = y
        self.board = board
        self.value = value
        player.pieces.append(self)

    def display(self):
        return self.icon()

    @abc.abstractmethod
    def can_move(self, x, y, ignoreillegal=False):
        pass

    def move(self, x, y):

        if self.can_move(x, y):
            self.board.cells[self.x][self.y] = None

            # If there is a piece where we move, we eat it
            if self.board.cells[x][y] is not None:
                self.board.cells[x][y].on_eat(self)

            self.board.cells[x][y] = self
            self.x = x
            self.y = y

    @abc.abstractmethod
    def get_possible_moves(self):
        pass

    def on_eat(self, piece):
        self.x = None
        self.y = None
        piece.player.eaten.append(self)

    def __str__(self):
        return str(self.icon()) + " at x="+str(self.x)+" y="+str(self.y)

    def icon(self):
        return "?"


class Pawn(Piece):

    def __init__(self, player, x=None, y=None):
        # Forward direction for the pawn, 1 if white, -1 if black
        self.direction = 1 if player.color == 0 else -1
        self.has_moved = False
        super().__init__(player, 1, x, y)

    def icon(self):
        if self.color == 0:
            return "♙"
        else:
            return "♟"

    def can_move(self, x, y, ignoreillegal=False):

        # The piece is not on the board
        if self.x is None or self.y is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(x, y):
            return False

        # This is the first move of the pawn and the cell is two cells in front of him
        if y == self.y + 2 * self.direction and not self.has_moved and x == self.x:
            # If one of the two cells in front of him is occupied
            if self.board.get_cell(x, y - self.direction) is not None or self.board.get_cell(x, y) is not None:
                return False
            else:
                # here it can move
                pass

        # The cell is not in the forward direction
        elif y != self.y + self.direction:
            return False

        # The cell in front of the pawn is occupied
        if x == self.x:
            if self.board.get_cell(x, y) is not None:
                return False

        elif x == self.x + 1 or x == self.x - 1:
            # Here, the cell is a diagonal, so there must be a piece in order to move here
            # If the cell is empty or the piece is owned by the same player, we cannot move here
            piece = self.board.get_cell(x, y)
            if piece is None or self.player == piece.player:
                return False

        else:
            # The cell is not in diagonal or in front of the pawn
            return False

        # Now, we check if the move is illegal
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.x, self.y, x, y)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return []

        # Every cell where the pawn could move
        allowed = [(self.x + i, self.y + self.direction) for i in range(-1, 2)]
        if not self.has_moved:
            allowed.append((self.x, self.y + 2*self.direction))

        # Check if they can move in the possible cells
        possible = []
        for c in allowed:
            if self.can_move(c[0], c[1]):
                possible.append(c)
        return possible

    def move(self, x, y):
        if self.can_move(x, y):

            super().move(x, y)
            self.has_moved = True

            # We check if the pawn can promote
            if self.y == 0 or self.y == self.board.shape[0] - 1:
                # TODO: Ask for promotion
                # Fix issue with icon not being set because icon is a property ?
                print("Promote pawn to :")
                print("1: Knight   2: Bishop   3: Rook   4: Queen")
                choice = None
                while choice is None:
                    try:
                        choice = int(input("Choice : "))
                        if choice not in (1, 2, 3, 4):
                            raise Exception
                    except:
                        choice = None
                        print("Please enter a valid choice !")
                piece_type = [Knight, Bishop, Rook, Queen][choice - 1]

                # Override instance methods to the ones of the piece promoted to
                self.icon = types.MethodType(piece_type.icon, self)
                self.display = types.MethodType(piece_type.display, self)
                self.can_move = types.MethodType(piece_type.can_move, self)
                self.get_possible_moves = types.MethodType(piece_type.get_possible_moves, self)
                self.move = types.MethodType(piece_type.move, self)

    def on_eat(self, piece):
        self.icon = types.MethodType(Pawn.icon, self)
        self.display = types.MethodType(Pawn.display, self)
        super().on_eat(piece)


class Rook(Piece):

    def __init__(self, player, x=None, y=None):
        self.has_moved = False
        super().__init__(player, 5, x, y)

    def move(self, x, y):
        if self.can_move(x, y):
            super(Rook, self).move(x, y)
            self.has_moved = True

    def icon(self):
        if self.color == 0:
            return "♖"
        else:
            return "♜"

    def can_move(self, x, y, ignoreillegal=False):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(x, y):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(x, y)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if x == self.x and y == self.y:
            return False

        # Column
        if x == self.x:
            # We check if the path is not blocked by another piece
            if y > self.y:
                direction = 1
            else:
                direction = -1

            for line in range(self.y + direction, y, direction):
                if self.board.get_cell(self.x, line) is not None:
                    return False
        # Line
        elif y == self.y:
            # We check if the path is not blocked by another piece
            if x > self.x:
                direction = 1
            else:
                direction = -1

            for col in range(self.x + direction, x, direction):
                if self.board.get_cell(col, self.y) is not None:
                    return False
        else:
            return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.x, self.y, x, y)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return []

        possible = []
        for col in (1, -1):
            i = 1
            while self.can_move(self.x + i * col, self.y):
                possible.append((self.x + i * col, self.y))
                i += 1

        for line in (1, -1):
            i = 1
            while self.can_move(self.x, self.y + i * line):
                possible.append((self.x, self.y + i * line))
                i += 1

        return possible


class Bishop(Piece):

    def __init__(self, player, x=None, y=None):
        super().__init__(player, 3, x, y)

    def icon(self):
        if self.color == 0:
            return "♗"
        else:
            return "♝"

    def can_move(self, x, y, ignoreillegal=False):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(x, y):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(x, y)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if x == self.x and y == self.y:
            return False

        # The piece is not in a diagonal
        if x-y != self.x - self.y and x+y != self.x + self.y:
            return False

        # We check if the path is not blocked by another piece
        if y > self.y:
            ydir = 1
        else:
            ydir = -1

        if x > self.x:
            xdir = 1
        else:
            xdir = -1

        i = 1
        while self.x + i * xdir != x and self.x + i * xdir != y:
            if self.board.get_cell(self.x + i * xdir, self.y + i * ydir) is not None:
                return False
            i += 1

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.x, self.y, x, y)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return []

        possible = []
        for xdir in (1, -1):
            for ydir in (1, -1):
                i = 1
                while self.can_move(self.x + i * xdir, self.y + i * ydir):
                    possible.append((self.x + i * xdir, self.y + i * ydir))
                    i += 1
        return possible


class Queen(Piece):

    def __init__(self, player, x=None, y=None):
        super().__init__(player, 9, x, y)

    def icon(self):
        if self.color == 0:
            return "♕"
        else:
            return "♛"

    def can_move(self, x, y, ignoreillegal=False):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(x, y):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(x, y)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if x == self.x and y == self.y:
            return False

        # The piece is in a diagonal
        if x - y == self.x - self.y or x + y == self.x + self.y:

            # We check if the path is not blocked by another piece
            if y > self.y:
                ydir = 1
            else:
                ydir = -1

            if x > self.x:
                xdir = 1
            else:
                xdir = -1

            i = 1
            while self.x + i * xdir != x and self.x + i * xdir != y:
                if self.board.get_cell(self.x + i * xdir, self.y + i * ydir) is not None:
                    return False
                i += 1

        # Column
        elif x == self.x:
            # We check if the path is not blocked by another piece
            if y > self.y:
                direction = 1
            else:
                direction = -1

            for line in range(self.y + direction, y, direction):
                if self.board.get_cell(self.x, line) is not None:
                    return False
        # Line
        elif y == self.y:
            # We check if the path is not blocked by another piece
            if x > self.x:
                direction = 1
            else:
                direction = -1

            for col in range(self.x + direction, x, direction):
                if self.board.get_cell(col, self.y) is not None:
                    return False

        else:
            return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.x, self.y, x, y)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return []

        possible = []

        # Columns
        for col in (1, -1):
            i = 1
            while self.can_move(self.x + i * col, self.y):
                possible.append((self.x + i * col, self.y))
                i += 1

        # Lines
        for line in (1, -1):
            i = 1
            while self.can_move(self.x, self.y + i * line):
                possible.append((self.x, self.y + i * line))
                i += 1

        # Diagonals
        for xdir in (1, -1):
            for ydir in (1, -1):
                i = 1
                while self.can_move(self.x + i * xdir, self.y + i * ydir):
                    possible.append((self.x + i * xdir, self.y + i * ydir))
                    i += 1

        return possible


class Knight(Piece):

    def __init__(self, player, x=None, y=None):
        super().__init__(player, 3, x, y)

    def icon(self):
        if self.color == 0:
            return "♘"
        else:
            return "♞"

    @property
    def _allowed_coordinates(self):
        return [
            (self.x + 1, self.y + 2), (self.x + 1, self.y - 2),
            (self.x - 1, self.y + 2), (self.x - 1, self.y - 2),
            (self.x + 2, self.y + 1), (self.x + 2, self.y - 1),
            (self.x - 2, self.y + 1), (self.x - 2, self.y - 1)
        ]

    def can_move(self, x, y, ignoreillegal=False):

        # The piece is not on the board
        if self.x is None or self.y is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(x, y):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(x, y)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if x == self.x and y == self.y:
            return False

        # The piece is not in an allowed place :
        if (x, y) not in self._allowed_coordinates:
            return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.x, self.y, x, y)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return []

        possible = []
        for cell in self._allowed_coordinates:
            if self.can_move(cell[0], cell[1]):
                possible.append(cell)
        return possible


class King(Piece):

    def __init__(self, player, x=None, y=None):
        player.king = self
        self.has_moved = False
        super().__init__(player, 0, x, y)

    def icon(self):
        if self.color == 0:
            return "♔"
        else:
            return "♚"

    def can_move(self, x, y, ignoreillegal=False):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return False

        # The cell is not on the board
        if not self.board.is_valid(x, y):
            return False

        # The cell is occupied by a piece of the player
        piece = self.board.get_cell(x, y)
        if piece is not None and piece.player == self.player:
            return False

        # The piece is not moving
        if x == self.x and y == self.y:
            return False

        # The piece is not in an allowed place :
        if not ((self.x - 1 <= x <= self.x + 1) and (self.y - 1 <= y <= self.y + 1)):
            return False

        # TODO: déplacer au dessus + bool pour pas check la cdt quand on roque ?
        # Roque
        if not self.has_moved:
            # roque droit
            p = self.board.get_cell(7, self.y)
            if type(p) == type(Rook) and p.player == self.player and not p.has_moved:
                # We check if the path is not blocked by another piece

                for col in range(self.x + 1, x, 1):
                    if self.board.get_cell(col, self.y) is not None:
                        return False

        # We check if the move puts the player in check :
        if ignoreillegal:
            return True
        return not self.board.is_illegal_move(self.player, self.x, self.y, x, y)

    def get_possible_moves(self):
        # The piece is not on the board
        if self.x is None or self.y is None:
            return []

        possible = []
        for x in range(self.x - 1, self.x + 2):
            for y in range(self.y - 1, self.y + 2):
                if self.can_move(x, y):
                    possible.append((x, y))
        return possible

    def move(self, x, y):
        if self.can_move(x, y):
            super(King, self).move(x, y)
            self.has_moved = True
