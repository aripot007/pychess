from typing import Type, Union
import pychess.ui.abstractui as abstractui
from pychess.board import Board
from pychess.pieces import *


class TermUI(abstractui.AbstractUI):

    def choice(self, title: str, choices: dict):
        print(title + "\n")
        labels, values = list(choices.keys()), list(choices.values())
        for i in range(len(labels)):
            print("  {:<4}{}".format(str(i + 1) + ".", labels[i]))
        print("")

        choice = None
        while choice is None:
            try:
                i = int(input("Choice : ")) - 1
                if i < 0 or i >= len(values):
                    raise Exception
                choice = values[i]
            except Exception:
                print("Please enter a valid choice !")
                choice = None

        return choice

    def input(self, msg="") -> str:
        return input(msg)

    def print(self, msg: str) -> None:
        print(msg)

    def promote_dialog(self, piece: Piece) -> Piece:
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
        return piece_type

    def display_board(self, board: Board) -> None:
        board.print_grid()

    def show_possible_moves(self, board: Board, row: int, col: int) -> None:
        board.print_possible_moves(row, col)
