import re
from pychess.player import *
import pychess.pieces as pieces

class Board:

    def __init__(self, shape=(8, 8), white=None, black=None, en_passant=None):
        # shape : (ranks, files)
        self.shape = shape

        # debug
        self.debug = False

        # The squares are stored from white's perspective, from rank 1 to 8 and file a to h, with cells[0][0] being the square a1 and cells[7,7] being the square h8
        self.ranks = [[None for _ in range(shape[1])] for _ in range(shape[0])]
        self.en_passant = en_passant
        self.turn = COLOR_WHITE  # White's turn
        self.halfmove_clock = 0
        self.fullmove_nb = 1
        if white is None:
            white = Player(COLOR_WHITE)
        if black is None:
            black = Player(COLOR_BLACK)
        self.white = white
        self.black = black
        self.players = [white, black]
        self.__init_grid_str()

    @classmethod
    def from_fen(cls, fen):
        """
        Create a board from a FEN string.
        """
        board = Board()

        # Split the string in the corresponding groups

        m = re.compile(r"^((?:[p,n,b,r,q,k,1-8]{1,8}/?){8}) ([w,b]) (-|(?:k?q?){2}) (-|[a-h][1-8]) ([0-9]+) ([0-9]+)", re.IGNORECASE)
        g = m.search(fen)
        if g:
            board_str = g.group(1)
            turn = g.group(2)
            castling = g.group(3)
            en_passant = g.group(4)
            halfmove_clock = int(g.group(5))
            fullmove_nb = int(g.group(6))
        else:
            raise ValueError("Invalid FEN String")

        # Create the pieces and place them on the board
        ranks = board_str.split("/")
        if len(ranks) != 8:
            raise ValueError("Invalid pieces position")

        pieces_types = {
            "P": pieces.Pawn,
            "N": pieces.Knight,
            "B": pieces.Bishop,
            "R": pieces.Rook,
            "Q": pieces.Queen,
            "K": pieces.King
        }

        for y in range(len(ranks)):
            file = 0
            rank = ranks[y]
            for char in rank:

                if char.isdigit():
                    # We skip the number of squares specified
                    file += int(char)
                else:
                    # We find the corresponding piece:
                    piece_type = pieces_types.get(char.upper())

                    # We get the player of the piece :
                    player = board.white if char.isupper() else board.black

                    # We add the piece to the board at the corresponding position
                    board.add_piece(piece_type(player), 7-y, file)

                    file += 1

            if file != 8:
                # Something went wrong : not enough or too many squares in this rank
                raise ValueError("Invalid number of squares on rank "+str(y + 1)+" ('"+rank+"'). Got "+str(file + 1)+" squares instead of 8")

        # Castling
        # TODO: Better castling checks
        if castling == "-":  # No castling
            if board.white.king is not None:
                board.white.king.has_moved = True
            if board.black.king is not None:
                board.black.king.has_moved = True
        else:
            # White king side (h1)
            rook = board.get_cell(0,7)
            if "K" not in castling and rook is not None and isinstance(rook, pieces.Rook):
                rook.has_moved = True

            # White queen side (a1)
            rook = board.get_cell(0, 0)
            if "Q" not in castling and rook is not None and isinstance(rook, pieces.Rook):
                rook.has_moved = True

            # Black king side (h8)
            rook = board.get_cell(7, 7)
            if "k" not in castling and rook is not None and isinstance(rook, pieces.Rook):
                rook.has_moved = True

            # Black queen side (a8)
            rook = board.get_cell(7, 0)
            if "q" not in castling and rook is not None and isinstance(rook, pieces.Rook):
                rook.has_moved = True

        board.turn = 0 if turn == "w" else 1
        board.halfmove_clock = halfmove_clock
        board.fullmove_nb = fullmove_nb

        if en_passant == "-":
            board.en_passant = None
        else:
            board.en_passant = (int(en_passant[1]) - 1, "abcdefgh".index(en_passant[0]))

        return board

    def to_fen(self):
        # Encode position
        position = ""
        for r in range(self.shape[0] - 1, -1, -1):
            rank = self.ranks[r]
            empty = 0
            for piece in rank:
                if piece is None:
                    empty += 1
                else:
                    # If there were empty cells, we write them
                    if empty != 0:
                        position += str(empty)
                        empty = 0
                    position += piece.san
            if empty != 0:
                position += str(empty)
            position += "/"

        # Remove the last /
        position = position[:-1]

        turn = "w" if self.turn == COLOR_WHITE else "b"

        castling = ""
        # TODO: Better checks for castling
        # White castling
        if self.white.king is not None and not self.white.king.has_moved:
            # King side (h1)
            rook = self.ranks[0][7]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "K"

            # Queen side (a1)
            rook = self.ranks[0][0]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "Q"

        # Black castling
        if self.black.king is not None and not self.black.king.has_moved:
            # King side (h8)
            rook = self.ranks[7][7]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "k"

            # Queen side (a8)
            rook = self.ranks[7][0]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "q"

        if castling == "":
            castling = "-"

        if self.en_passant is not None:
            en_passant = "abcdefgh"[self.en_passant[1]] + str(self.en_passant[0] + 1)
        else:
            en_passant = "-"
        halfmove = str(self.halfmove_clock)
        fullmove_nb = str(self.fullmove_nb)

        fen = position + " " + turn + " " + castling + " " + en_passant + " " + halfmove + " " + fullmove_nb

        return fen

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

    def get_cell(self, rank, file):
        return self.ranks[rank][file]

    def is_valid(self, rank, file):
        return 0 <= rank < self.shape[0] and 0 <= file < self.shape[0]

    def is_check(self, player, ignorepiece=None):
        king_row = player.king.row
        king_col = player.king.col
        for p in self.players:
            if p == player:
                continue
            for piece in p.pieces:
                if piece == ignorepiece:
                    continue
                if piece.can_move(king_row, king_col, ignoreillegal=True):
                    if self.debug:
                        print("Piece "+str(piece)+ " at "+str(piece.row)+ " " + str(piece.col) + " is checking king "+str(player.color))
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

    def is_illegal_move(self, player, row, col, dest_row, dest_col):
        """
        Check if a move puts the player in check
        :param player: The player performing the move
        :param row: The piece's x  position
        :param col: The piece's y position
        :param dest_row: The destination cell's x
        :param dest_col: The destination cell's y
        :return: True if the move is illegal, otherwise False.
        """
        # We move the piece and keep in dest_piece the piece in the destination cell
        dest_piece, self.ranks[row][col], self.ranks[dest_row][dest_col] = self.ranks[dest_row][dest_col], None, self.ranks[row][col]
        piece = self.ranks[dest_row][dest_col]
        piece.row = dest_row
        piece.col = dest_col

        check = self.is_check(player, ignorepiece=dest_piece)

        # We revert the board to it's original state
        self.ranks[row][col], self.ranks[dest_row][dest_col] = self.ranks[dest_row][dest_col], dest_piece
        piece = self.ranks[row][col]
        piece.row = row
        piece.col = col

        return check

    def _format_grid(self, printable_grid, label=False):
        """format the given grid to a printabe format"""
        # Rearange the grid
        str_list = []
        for r in range(len(printable_grid) - 1, -1, -1):
            rank = printable_grid[r]
            for square in rank:
                str_list.append(square)

        if label:
            return self.grid_str_label.format(*str_list)
        return self.grid_str.format(*str_list)

    def print_grid(self, label=True):
        """Print the grid with all the pieces"""
        printable_grid = [[" " for _ in range(self.shape[1])] for _ in range(self.shape[0])]
        for rank in range(self.shape[0]):
            for file in range(self.shape[1]):
                if self.ranks[rank][file] is not None:
                    printable_grid[rank][file] = self.ranks[rank][file].icon()

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

                    if self.ranks[col][line] is not None:
                        printable_grid[col][line] = self.ranks[col][line].icon()

                    if (col, line) in poss:
                        if self.ranks[col][line] is not None:
                            printable_grid[col][line] = "❌"
                        else:
                            printable_grid[col][line] = "●"

            print(self._format_grid(printable_grid, label))
            return

    def add_piece(self, piece, x, y):
        self.ranks[x][y] = piece
        piece.row = x
        piece.col = y
        piece.board = self

    def remove_piece(self, x, y):
        piece = self.ranks[x][y]
        self.ranks[x][y] = None
        piece.board = None
        piece.row = None
        piece.col = None

    def add_player(self, player):
        self.players.append(player)
        player.board = self

    def state_equals(self, other):
        return isinstance(other, Board) and self.__state_hash__() == other.__state_hash__()

    def __state_hash__(self):
        pos = ""
        for rank in self.ranks:
            for piece in rank:
                if piece is None:
                    pos += " "
                else:
                    pos += piece.san

        castling = ""
        # TODO: Better checks for castling
        # White castling
        if self.white.king is not None and not self.white.king.has_moved:
            # King side (h1)
            rook = self.ranks[0][7]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "K"

            # Queen side (a1)
            rook = self.ranks[0][0]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "Q"

        # Black castling
        if self.black.king is not None and not self.black.king.has_moved:
            # King side (h8)
            rook = self.ranks[7][7]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "k"

            # Queen side (a8)
            rook = self.ranks[7][0]
            if rook is not None and isinstance(rook, pieces.Rook) and not rook.has_moved:
                castling += "q"

        return hash((self.shape, pos, self.turn, castling, self.en_passant, self.halfmove_clock, self.fullmove_nb))

    def __repr__(self):
        return "<Board shape={}, state_hash='{}' fen='{}', white={}, black={}>".format(str(self.shape), str(self.__state_hash__()), self.to_fen(), self.white
                                                                                       , self.black)
