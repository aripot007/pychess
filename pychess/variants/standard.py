from pychess.variants.variant import Variant
import pychess.ui
from pychess.player import Player
from pychess.board import Board
import pychess.pieces as pieces
import pychess.signals as signals
import re


class StandardVariant(Variant):

    NAME = "Classic"
    DESC = "A classic chess game"

    def __init__(self):
        self.ui = pychess.ui.get_default_ui()
        self.white = None
        self.black = None
        self.board = None

        def handle_pawn_promotion(sender, **kwargs):
            self.__on_pawn_promotion(sender, **kwargs)
        self.handle_pawn_protection = handle_pawn_promotion
        signals.PAWN_PROMOTION.connect(handle_pawn_promotion)

    def __on_pawn_promotion(self, sender: pieces.Pawn, **kwargs):
        piece_type = self.ui.promote_dialog(sender)
        sender.promote(piece_type)

    def setup(self):
        # Create players
        white_name = self.ui.input("White player name : ")
        black_name = self.ui.input("Black player name : ")

        self.white = Player(pychess.player.COLOR_WHITE, white_name)
        self.black = Player(pychess.player.COLOR_BLACK, black_name)

        # Create the board
        self.board = Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", white=self.white, black=self.black)

    def start(self):
        gameover = False
        if self.board.turn == pychess.player.COLOR_WHITE:
            player, spect = self.white, self.black
        else:
            player, spect = self.black, self.white

        positions = dict()
        while not gameover:
            turn = True
            self.ui.display_board(self.board)
            self.ui.print(player.name + "'s turn : ")
            while turn:

                txt = self.ui.input(player.name + "> ")

                txt = txt.split(" ")
                cmd = txt[0]

                if cmd == "help":
                    if len(txt) == 1:
                        print("Available commands :\n")
                        print(" help [command]: Display help about a command")
                        print(" board : Print the board")
                        print(" select [cell] : Select the piece at the given coordinates (alias : sel, s)")
                        print(" move [cell] : Move the selected piece to the given coordinates (alias : m)")
                        print(" sm [cell] [cell] : Select the piece at the first given cell and move it to the second.")
                        print(" fen : Get the FEN string for the board.")
                        continue
                    else:
                        if txt[1] in ("select", "sel", "s"):
                            print("Help : select\n")
                            print("Syntax : select [cell]\n")
                            print("Select the piece at the given coordinates. The cell coordinate must be given like this : e4")
                            print("Ex : select e2")

                        elif txt[1] in ("move", "m"):
                            print("Help : move\n")
                            print("Syntax : move [cell]\n")
                            print("Move the selected piece at the given coordinates. The cell coordinate must be given like this : e4")
                            print("To select a piece, use the command 'select [cell]'.")
                            print("Ex : move a3")

                        elif txt[1] == "board":
                            print("Help : board\n")
                            print("Syntax : board\n")
                            print("Print the board on the screen")

                        elif txt[1] == "help":
                            print("Help : help\n")
                            print("Syntax : help [cmd]\n")
                            print(
                                "Without any argument, print the list of available commands. If a command is specified, prints the help of the specified command.")

                        elif txt[1] == "sm":
                            print("Help : sm\n")
                            print("Syntax : sm [cell] [cell]\n")
                            print(
                                "Select the piece at the given coordinates, then moves it at the second coordinates. The cells coordinates must be given like this : e4")
                            print("Ex : sm e2 e4")

                        else:
                            print("Error : the command '" + txt[1] + "' does not exist.")

                        continue

                elif cmd == "fen":
                    self.ui.print(self.board.to_fen())
                    continue

                elif cmd == "board":
                    self.ui.display_board(self.board)
                    continue

                elif cmd in ("select", "sel", "s"):
                    if len(txt) == 1:
                        self.ui.print("Syntax : select [cell]")
                        continue
                    else:
                        cell_str = txt[1]
                        if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                            self.ui.print("Please enter a valid coordinate (ex: e4)")
                            continue

                        rank = int(cell_str[1:]) - 1
                        file = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())

                        if not self.board.is_valid(rank, file):
                            self.ui.print("This cell does not exist !")
                            continue

                        piece = self.board.get_cell(rank, file)
                        if piece is None:
                            self.ui.print("There is no piece on this cell !")
                            continue

                        if piece.player != player:
                            self.ui.print("You can only select your pieces !")
                            continue

                        player.selected = piece
                        self.ui.show_possible_moves(self.board, rank, file)
                        self.ui.print("selected : " + piece.icon())
                        continue

                elif cmd in ("move", "m"):
                    if len(txt) == 1:
                        self.ui.print("Syntax : move [cell]")
                        continue
                    else:
                        piece = player.selected

                        if piece is None:
                            self.ui.print("Please select a piece with 'select [cell]'.")
                            continue

                        cell_str = txt[1]
                        if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                            self.ui.print("Please enter a valid coordinate (ex: e4)")
                            continue

                        rank = int(cell_str[1:]) - 1
                        file = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())

                        if not self.board.is_valid(rank, file):
                            self.ui.print("This cell does not exist !")
                            continue

                        if not piece.can_move(rank, file):
                            self.ui.print("This is not a valid move !")
                            continue

                        piece.move(rank, file)
                        player.selected = None
                        turn = False

                elif cmd == "sm":
                    if len(txt) != 3:
                        self.ui.print("Syntax : sm [cell] [cell]")
                        continue
                    else:
                        cell_str = txt[1]
                        if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                            self.ui.print("Please enter a valid coordinate (ex: e4)")
                            continue

                        rank = int(cell_str[1:]) - 1
                        file = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())

                        if not self.board.is_valid(rank, file):
                            self.ui.print("This cell does not exist !")
                            continue

                        piece = self.board.get_cell(rank, file)
                        if piece is None:
                            self.ui.print("There is no piece on this cell !")
                            continue

                        if piece.player != player:
                            self.ui.print("You can only select your pieces !")
                            continue

                        cell_str = txt[2]
                        if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                            self.ui.print("Please enter a valid coordinate (ex: e4)")
                            continue

                        rank = int(cell_str[1:]) - 1
                        file = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())

                        if not self.board.is_valid(rank, file):
                            self.ui.print("This cell does not exist !")
                            continue

                        if not piece.can_move(rank, file):
                            self.ui.print("This is not a valid move !")
                            continue

                        piece.move(rank, file)
                        turn = False

                else:
                    self.ui.print("Unknown command '" + cmd + "'. Type 'help' for a list of available commands.")
                    continue

            # Turn is over, we chek if the game is over:
            if not spect.can_move():
                if spect.is_check():
                    # Checkmate
                    gameover = True
                    self.ui.display_board(self.board)
                    self.ui.print("Checkmate !")
                    self.ui.print(player.name + " wins !")
                else:
                    # Pat
                    gameover = True
                    self.ui.display_board(self.board)
                    self.ui.print("Pat !")
                    self.ui.print("Draw !")

            # We check if there is a draw :
            # 75 moves without a pawn move or a piece take:
            if self.board.halfmove_clock >= 75:
                gameover = True
                self.ui.display_board(self.board)
                self.ui.print("Draw ! (50 moves without capture or pawn move)")

            # We check if a position was repeated 3 times
            pos_hash = str(self.board.__position_hash__())
            if positions.get(pos_hash) is None:
                positions[pos_hash] = 0
            positions[pos_hash] += 1

            if positions[pos_hash] >= 3:
                gameover = True
                self.ui.display_board(self.board)
                self.ui.print("Draw ! (Repetition)")

            self.board.next_turn()
            player, spect = spect, player

    def stop(self):
        pass
