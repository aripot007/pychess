import pytest
from pychess.board import Board
from pychess.pieces import *
from pychess.player import Player


class TestBoardFen:

    def setup_method(self):
        self.white = Player(COLOR_WHITE, "White")
        self.black = Player(COLOR_BLACK, "Black")
        self.board = Board(white=self.white, black=self.black)

        self.board.add_piece(King(self.white), 0, 4)
        self.board.add_piece(King(self.black), 7, 4)

        self.board.add_piece(Pawn(self.white), 3, 4)
        self.board.add_piece(Rook(self.white), 0, 7)
        rook = Rook(self.white)
        self.board.add_piece(rook, 0, 0)
        rook.has_moved = True

        self.board.add_piece(Queen(self.black), 1, 6)
        self.board.add_piece(Bishop(self.black), 7, 0)
        self.board.add_piece(Rook(self.black), 7, 7)
        self.board.add_piece(Knight(self.black), 4, 3)
        self.board.en_passant = (2, 4)
        self.board.halfmove_clock = 5
        self.board.fullmove_nb = 35

    def teardown_method(self):
        self.board = None
        self.white = None
        self.black = None

    def test_empty_fen_raises_exception(self):
        with pytest.raises(ValueError):
            Board.from_fen("")

    def test_invalid_fen_raises_exception(self):
        with pytest.raises(ValueError):
            Board.from_fen("rnjeijzjeir")

    def test_invalid_fen_piece_placement_raises_exception(self):
        with pytest.raises(ValueError):
            # Here, the pieces on the second row does not exist
            Board.from_fen("rnbqkbnr/easze/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        with pytest.raises(ValueError):
            # Here, there is too many pieces on rank 8
            Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNRP w KQkq - 0 1")

        with pytest.raises(ValueError):
            # Here, there is too few pieces on rank 2
            Board.from_fen("rnbqkbnr/pppppp/8/8/8/8/PPPPPPPP/RNBQKBNRP w KQkq - 0 1")

        with pytest.raises(ValueError):
            # Here, there is too few squares on rank 2
            Board.from_fen("rnbqkbnr/p5p/8/8/8/8/PPPPPPPP/RNBQKBNRP w KQkq - 0 1")

        with pytest.raises(ValueError):
            # Here, there is not enough ranks
            Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/ w KQkq - 0 1")

        with pytest.raises(ValueError):
            # Same as above, but without the trailing slash
            Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w KQkq - 0 1")

    def test_invalid_fen_turn_raises_exception(self):
        with pytest.raises(ValueError):
            # Here, the turn is missing
            Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR KQkq - 0 1")

    def test_invalid_fen_castling_exception(self):
        with pytest.raises(ValueError):
            # Here, the castling information is wrong (a)
            Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w a - 0 1")

    def test_to_fen(self):
        assert self.board.to_fen() == "b3k2r/8/8/3n4/4P3/8/6q1/R3K2R w Kk e3 5 35"

    def test_from_fen(self):
        board_2 = Board.from_fen("b3k2r/8/8/3n4/4P3/8/6q1/R3K2R w Kk e3 5 35")
        assert self.board.state_equals(board_2)


class TestBoard:

    def setup_method(self):
        self.white = Player(COLOR_WHITE, "White")
        self.black = Player(COLOR_BLACK, "Black")
        self.board = Board(white=self.white, black=self.black)

        self.board.add_piece(King(self.white), 0, 4)
        self.board.add_piece(King(self.black), 7, 4)

        self.board.add_piece(Pawn(self.white), 3, 4)
        self.board.add_piece(Rook(self.white), 0, 7)
        rook = Rook(self.white)
        self.board.add_piece(rook, 0, 0)
        rook.has_moved = True

        self.board.add_piece(Queen(self.black), 1, 6)
        self.board.add_piece(Bishop(self.black), 7, 0)
        self.board.add_piece(Rook(self.black), 7, 7)
        self.board.add_piece(Knight(self.black), 4, 3)
        self.board.en_passant = (2, 4)
        self.board.halfmove_clock = 5
        self.board.fullmove_nb = 35

        self.white2 = Player(COLOR_WHITE, "White 2")
        self.black2 = Player(COLOR_BLACK, "Black 2")
        self.board2 = Board(white=self.white2, black=self.black2)

        self.board2.add_piece(King(self.white2), 0, 4)
        self.board2.add_piece(King(self.black2), 7, 4)

        self.board2.add_piece(Pawn(self.white2), 3, 4)
        self.board2.add_piece(Rook(self.white2), 0, 7)
        rook2 = Rook(self.white2)
        self.board2.add_piece(rook, 0, 0)
        rook2.has_moved = True

        self.board2.add_piece(Queen(self.black2), 1, 6)
        self.board2.add_piece(Bishop(self.black2), 7, 0)
        self.board2.add_piece(Rook(self.black2), 7, 7)
        self.board2.add_piece(Knight(self.black2), 4, 3)
        self.board2.en_passant = (2, 4)
        self.board2.halfmove_clock = 5
        self.board2.fullmove_nb = 35

    def test_state_equals(self):
        assert self.board.state_equals(self.board2)

    def test_self_equals(self):
        assert self.board.state_equals(self.board)

    def test_state_not_equals(self):
        self.board2.add_piece(Pawn(self.white2), 5, 5)
        assert not self.board.state_equals(self.board2)

    def test_square_valid(self):
        assert self.board.is_valid(0, 0)
        assert self.board.is_valid(7, 7)
        assert self.board.is_valid(5, 3)

    def test_square_invalid(self):
        assert not self.board.is_valid(-1, 0)
        assert not self.board.is_valid(8, 3)
        assert not self.board.is_valid(5, -10)
        assert not self.board.is_valid(10, 15)

    def test_add_piece(self):
        piece = Pawn(self.white)
        self.board.add_piece(piece, 3, 3)
        assert self.board.get_cell(3, 3) == piece
        assert piece.row == 3 and piece.col == 3
        assert piece.board == self.board

    def test_remove_piece(self):
        # Remove the white pawn in e4
        piece = self.board.get_cell(3, 4)
        self.board.remove_piece(3, 4)

        assert self.board.get_cell(3, 4) is None
        assert piece.board is None
        assert piece.row is None
        assert piece.col is None

    def test_illegal_move(self):
        # Try to move white's king in front of black's queen
        assert self.board.is_illegal_move(self.white, 0, 4, 0, 5)

    def test_legal_move(self):
        # Try to move the rook from a1 to a2
        assert not self.board.is_illegal_move(self.white, 0, 0, 1, 0)

    def test_check(self):
        assert not self.board.is_check(self.white)
        # Add a rook on b1, checking white's king
        self.board.add_piece(Rook(self.black), 0, 1)
        assert self.board.is_check(self.white)

    def test_checkmate(self):
        # Black checkmates White with 2 rooks
        board = Board()
        board.add_piece(Rook(board.black), 0, 0)
        board.add_piece(Rook(board.black), 1, 7)
        board.add_piece(King(board.white), 0, 4)
        board.add_piece(King(board.black), 7, 4)
        board.add_piece(Pawn(board.white), 3, 3)

        assert not board.is_checkmate(board.black)
        assert board.is_checkmate(board.white)

    def test_pat(self):
        # White is pat
        board = Board()
        board.add_piece(Rook(board.black), 1, 0)
        board.add_piece(Knight(board.black), 2, 4)
        board.add_piece(King(board.white), 0, 4)
        board.add_piece(King(board.black), 6, 2)
        board.add_piece(Pawn(board.white), 5, 2)

        assert not board.is_pat(board.black)
        assert board.is_pat(board.white)


class TestBoardDisplay:
    # Todo: test display methods
    pass
