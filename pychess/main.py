from pychess.pieces import *
from pychess.board import Board
from pychess.player import Player
import re


name = input("Player 1 : ")
p1 = Player(0, name)

name = input("Player 2 : ")
p2 = Player(1, name)

board = Board((10,12))
board.add_player(p1)
board.add_player(p2)

# Populate board with pieces :

for player, row1, row2 in [(p1, 0, 1), (p2, 7, 6)]:

    # Pawns
    for x in range(8):
        board.add_piece(Pawn(player), x, row2)

    board.add_piece(Rook(player), 0, row1)
    board.add_piece(Rook(player), 7, row1)

    board.add_piece(Knight(player), 1, row1)
    board.add_piece(Knight(player), 6, row1)

    board.add_piece(Bishop(player), 2, row1)
    board.add_piece(Bishop(player), 5, row1)

    board.add_piece(Queen(player), 3, row1)
    board.add_piece(King(player), 4, row1)

gameover = False
player, spect = p1, p2
while not gameover:
    turn = True
    board.print_grid()
    print(player.name+"'s turn : ")
    while turn:

        txt = input(player.name + "> ")

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
                    print(
                        "Move the selected piece at the given coordinates. The cell coordinate must be given like this : e4")
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
                    print("Select the piece at the given coordinates, then moves it at the second coordinates. The cells coordinates must be given like this : e4")
                    print("Ex : sm e2 e4")

                else:
                    print("Error : the command '" + txt[1] + "' does not exist.")

                continue

        elif cmd == "board":
            board.print_grid(True)
            continue

        elif cmd in ("select", "sel", "s"):
            if len(txt) == 1:
                print("Syntax : select [cell]")
                continue
            else:
                cell_str = txt[1]
                if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                    print("Please enter a valid coordinate (ex: e4)")
                    continue

                x = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())
                y = int(cell_str[1:]) -1

                if not board.is_valid(x, y):
                    print("This cell does not exist !")
                    continue

                piece = board.get_cell(x, y)
                if piece is None:
                    print("There is no piece on this cell !")
                    continue

                if piece.player != player:
                    print("You can only select your pieces !")
                    continue

                player.selected = piece
                board.print_possible_moves(x, y, True)
                print("selected : " + piece.icon())
                continue

        elif cmd in ("move", "m"):
            if len(txt) == 1:
                print("Syntax : move [cell]")
                continue
            else:
                piece = player.selected

                if piece is None:
                    print("Please select a piece with 'select [cell]'.")
                    continue

                cell_str = txt[1]
                if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                    print("Please enter a valid coordinate (ex: e4)")
                    continue

                x = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())
                y = int(cell_str[1:]) - 1

                if not board.is_valid(x, y):
                    print("This cell does not exist !")
                    continue

                if not piece.can_move(x, y):
                    print("This is not a valid move !")
                    continue

                piece.move(x, y)
                player.selected = None
                board.print_grid(True)
                turn = False

        elif cmd == "sm":
            if len(txt) != 3:
                print("Syntax : sm [cell] [cell]")
                continue
            else:
                cell_str = txt[1]
                if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                    print("Please enter a valid coordinate (ex: e4)")
                    continue

                x = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())
                y = int(cell_str[1:]) -1

                if not board.is_valid(x, y):
                    print("This cell does not exist !")
                    continue

                piece = board.get_cell(x, y)
                if piece is None:
                    print("There is no piece on this cell !")
                    continue

                if piece.player != player:
                    print("You can only select your pieces !")
                    continue

                cell_str = txt[2]
                if re.match(r"^[a-z|A-Z]\d{1,2}$", cell_str) is None:
                    print("Please enter a valid coordinate (ex: e4)")
                    continue

                x = "abcdefghijklmnopqrstuvwxyz".find(cell_str[0].lower())
                y = int(cell_str[1:]) - 1

                if not board.is_valid(x, y):
                    print("This cell does not exist !")
                    continue

                if not piece.can_move(x, y):
                    print("This is not a valid move !")
                    continue

                piece.move(x, y)
                board.print_grid(True)
                turn = False

        else:
            print("Unknown command '"+cmd+"'. Type 'help' for a list of available commands.")
            continue

    # Turn is over, we chek if the game is over:
    if not spect.can_move():
        if spect.is_check():
            # Checkmate
            gameover = True
            print("Checkmate !")
            print(player.name + " wins !")
        else:
            # Pat
            gameover = True
            print("Pat !")
            print("Draw !")

    player, spect = spect, player

