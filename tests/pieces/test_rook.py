from pychess.board import Board


class TestRookMoves:

    def setup_method(self):
        self.board = Board.from_fen("r3k3/4r3/2r2p2/8/8/1PR5/4R3/4K2R w Kq - 0 1")

    def teardown_method(self):
        self.board = None

    def test_can_move_row_col(self):
        # White rook on h1
        assert self.board.get_cell(0, 7).can_move(7, 7)  # Forward
        assert self.board.get_cell(0, 7).can_move(0, 6)  # Left
        # White rook on c3
        assert self.board.get_cell(2, 2).can_move(2, 4)  # Right
        assert self.board.get_cell(2, 2).can_move(0, 2)  # Backward

        # Black rook on a8
        assert self.board.get_cell(7, 0).can_move(0, 0)  # Backward
        assert self.board.get_cell(7, 0).can_move(7, 2)  # Right
        # Black rook on c6
        assert self.board.get_cell(5, 2).can_move(7, 2)  # Forward
        assert self.board.get_cell(5, 2).can_move(5, 0)  # Left

    def test_move_blocked(self):
        # White rook on c3
        rook = self.board.get_cell(2, 2)
        assert not rook.can_move(2, 1)  # On white pawn
        assert not rook.can_move(2, 0)  # Behind white pawn
        assert not rook.can_move(7, 1)  # Behind black rook

        # Black rook on c6
        rook = self.board.get_cell(5, 2)
        assert not rook.can_move(5, 5)  # On black pawn
        assert not rook.can_move(5, 7)  # Behind black pawn
        assert not rook.can_move(0, 2)  # Behind white rook

    def test_check_pin(self):
        # Check if illegal moves are prevented
        assert not self.board.get_cell(1, 4).can_move(1, 5)
        assert not self.board.get_cell(6, 4).can_move(6, 5)

    def test_take(self):
        assert self.board.get_cell(2, 2).can_move(5, 2)  # Takes black rook
        assert self.board.get_cell(6, 4).can_move(1, 4)  # Takes white rook

    def test_not_on_board(self):
        piece = self.board.get_cell(2, 2)
        self.board.remove_piece(2, 2)
        assert not piece.can_move(2, 3)

    def test_invalid_square(self):
        rook = self.board.get_cell(2, 2)
        assert not rook.can_move(3, 3)
        assert not rook.can_move(2, 8)
        assert not rook.can_move(-2, 2)

    def test_get_possible_moves(self):
        # White rook on c3
        rook = self.board.get_cell(2, 2)
        assert set(rook.get_possible_moves()) == {(2, 4), (1, 2), (2, 7), (4, 2), (2, 3), (0, 2), (2, 6), (3, 2), (2, 5), (5, 2)}

        # Black rook on c6
        rook = self.board.get_cell(5, 2)
        assert set(rook.get_possible_moves()) == {(6, 2), (5, 4), (5, 1), (4, 2), (5, 0), (7, 2), (2, 2), (5, 3), (3, 2)}
