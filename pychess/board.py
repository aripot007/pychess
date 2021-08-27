import re

class Board:

    def __init__(self, shape=(8, 8), players=[], en_passant=None):
        # shape : (lines, columns)
        self.shape = shape
        self.cells = [[None for _ in range(shape[0])] for _ in range(shape[1])]
        self.en_passant = en_passant
        self.players = players
        self.__init_grid_str()

    @classmethod
    def from_fen(self, fen):
        """
        Create a board from a FEN string.
        """
        board = Board()

        # Split the string in the corresponding groups
        m = re.compile("")
        groups = m.search(fen)
        if groups:
            pass
        else:



    def __init_grid_str(self):
        """
        Initialize the format strings for printing the board.
        grid_str : format string without labels
        grid_str_label : format string with labels
        """
        grid_str = "┌─────" + (self.shape[1] - 1) * "┬─────" + "┐\n"
        for i in range(self.shape[0] - 1):
            grid_str += "│  {}  " * self.shape[1] + "│\n"
            grid_str += "├─────" + (self.shape[1] - 1) * "┼─────" + "┤\n"
        grid_str += "│  {}  " * self.shape[1] + "│\n"
        grid_str += "└─────" + (self.shape[1] - 1) * "┴─────" + "┘\n"
        self.grid_str = grid_str

        grid_str_label = "   " + "   {}  ".format("A")
        for i in range(self.shape[1] - 1):
            grid_str_label += "   {}  ".format("BCDEFGHIJKLMNOPQRSTUVWXYZ"[i])

        grid_str_label += "\n   ┌─────" + (self.shape[1] - 1) * "┬─────" + "┐\n"
        for i in range(self.shape[0] - 1):
            grid_str_label += "{:<2} ".format(self.shape[0] - i) + "│  {}  " * self.shape[1] + "│\n"
            grid_str_label += "   ├─────" + (self.shape[1] - 1) * "┼─────" + "┤\n"

        grid_str_label += "1  " + "│  {}  " * self.shape[1] + "│\n"
        grid_str_label += "   └─────" + (self.shape[1] - 1) * "┴─────" + "┘\n"

        self.grid_str_label = grid_str_label

    def get_cell(self, col, line):
        return self.cells[col][line]

    def is_valid(self, col, line):
        return 0 <= col < self.shape[1] and 0 <= line < self.shape[0]

    def is_check(self, player, ignorepiece=None):
        king_x = player.king.x
        king_y = player.king.y
        for p in self.players:
            if p == player:
                continue
            for piece in p.pieces:
                if piece == ignorepiece:
                    continue
                if piece.can_move(king_x, king_y, ignoreillegal=True):
                    return True
        return False

    def is_checkmate(self, player):
        if self.is_check(player) and not player.can_move():
            return True
        else:
            return False

    def is_pat(self, player):
        if not self.is_check(player) and not player.can_move():
            return True
        else:
            return False

    def is_illegal_move(self, player, x1, y1, x2, y2):
        """
        Check if a move puts the player in check
        :param player: The player performing the move
        :param x1: The piece's x  position
        :param y1: The piece's y position
        :param x2: The destination cell's x
        :param y2: The destination cell's y
        :return: True if the move is illegal, otherwise False.
        """
        # We move the piece and keep in dest_piece the piece in the destination cell
        dest_piece, self.cells[x1][y1], self.cells[x2][y2] = self.cells[x2][y2], None, self.cells[x1][y1]
        piece = self.cells[x2][y2]
        piece.x = x2
        piece.y = y2

        check = self.is_check(player, ignorepiece=dest_piece)

        # We revert the board to it's original state
        self.cells[x1][y1], self.cells[x2][y2] = self.cells[x2][y2], dest_piece
        piece = self.cells[x1][y1]
        piece.x = x1
        piece.y = y1

        return check

    def _format_grid(self, printable_grid, label=False):
        """format the given grid to a printabe format"""
        str_list = []
        for line in range(self.shape[0] - 1, -1, -1):
            for col in printable_grid:
                str_list.append(col[line])

        if label:
            return self.grid_str_label.format(*str_list)
        return self.grid_str.format(*str_list)

    def print_grid(self, label=True):
        """Print the grid with all the pieces"""
        printable_grid = [[" " for _ in range(self.shape[0])] for _ in range(self.shape[1])]
        for col in range(self.shape[1]):
            for line in range(self.shape[0]):
                if self.cells[col][line] is not None:
                    printable_grid[col][line] = self.cells[col][line].icon()

        print(self._format_grid(printable_grid, label))
        return

    def print_possible_moves(self, x, y, label=True):
        """Print the grid with the possible moves of the piece at the x, y position"""
        piece = self.get_cell(x, y)
        if piece is None:
            self.print_grid(label)
            return
        else:
            poss = piece.get_possible_moves()

            printable_grid = [[" " for _ in range(self.shape[0])] for _ in range(self.shape[1])]

            for col in range(self.shape[1]):
                for line in range(self.shape[0]):

                    if self.cells[col][line] is not None:
                        printable_grid[col][line] = self.cells[col][line].icon()

                    if (col, line) in poss:
                        if self.cells[col][line] is not None:
                            printable_grid[col][line] = "❌"
                        else:
                            printable_grid[col][line] = "●"

            print(self._format_grid(printable_grid, label))
            return

    def add_piece(self, piece, x, y):
        self.cells[x][y] = piece
        piece.x = x
        piece.y = y
        piece.board = self

    def add_player(self, player):
        self.players.append(player)
        player.board = self
