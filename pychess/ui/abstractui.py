import abc
from pychess.pieces import Piece
from pychess.board import Board


class AbstractUI:

    @abc.abstractmethod
    def choice(self, title: str, choices: dict):
        """
        Ask the user to make a choice.
        :param title: The title of the choice
        :param choices: A dict with the keys being the labels of the choices and the values the choices that will be returned
        :return: The value choosen by the user
        """

    @abc.abstractmethod
    def input(self, msg="") -> str:
        """Get user input"""

    @abc.abstractmethod
    def print(self, msg: str) -> None:
        """Display a text to the user"""

    @abc.abstractmethod
    def promote_dialog(self, piece: Piece) -> Piece:
        """
        Show the promotion dialog for the given piece.
        :return: The piece type to promote to
        """

    @abc.abstractmethod
    def display_board(self, board: Board) -> None:
        """
        Display the given board to the user
        :param board: The board to display
        """
        # TODO: Add option to flip the board


    @abc.abstractmethod
    def show_possible_moves(self, board: Board, row: int, col: int) -> None:
        """
        Display the possible moves to the user
        :param board: The board to display
        :param row: The rank of the piece
        :param col: The file of the piece
        """
        # TODO: Add option to flip the board
