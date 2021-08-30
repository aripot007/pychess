from pychess.board import Board


class TestQueenMoves:

    def setup_method(self):
        self.board = Board.from_fen("k7/q7/8/2p1q1P1/8/2p1Q1P1/Q7/K7 w - - 0 1")
        self.wqueen = self.board.get_cell(2, 4)
        self.bqueen = self.board.get_cell(4, 4)
        self.pin_wqueen = self.board.get_cell(1, 0)
        self.pin_bqueen = self.board.get_cell(6, 0)

    def teardown_method(self):
        self.board = None

    def test_can_move_row_col(self):
        # White queen
        assert self.wqueen.can_move(3, 4)  # Forward
        assert self.wqueen.can_move(2, 3)  # Left
        assert self.wqueen.can_move(2, 5)  # Right
        assert self.wqueen.can_move(0, 4)  # Backward

        # Black queen
        assert self.bqueen.can_move(3, 4)  # Forward
        assert self.bqueen.can_move(4, 3)  # Left
        assert self.bqueen.can_move(4, 5)  # Right
        assert self.bqueen.can_move(7, 4)  # Backward

    def test_move_row_col_blocked(self):
        # White queen
        assert not self.wqueen.can_move(2, 6)  # On white pawn
        assert not self.wqueen.can_move(2, 0)  # Behind black pawn
        assert not self.wqueen.can_move(6, 4)  # Behind black queen

        # Black queen
        assert not self.bqueen.can_move(4, 2)  # On black pawn
        assert not self.bqueen.can_move(4, 0)  # Behind black pawn
        assert not self.bqueen.can_move(0, 4)  # Behind white queen

    def test_can_move_diagonal(self):
        # White queen
        assert self.wqueen.can_move(3, 5)  # Up right
        assert self.wqueen.can_move(3, 3)  # Up left
        assert self.wqueen.can_move(0, 2)  # Down left
        assert self.wqueen.can_move(0, 6)  # Down right

        # Black queen
        assert self.bqueen.can_move(7, 7)  # Up right
        assert self.bqueen.can_move(7, 1)  # Up left
        assert self.bqueen.can_move(3, 3)  # Down left
        assert self.bqueen.can_move(3, 5)  # Down right

    def test_move_diagonal_blocked(self):
        # White queen
        assert not self.wqueen.can_move(4, 6)  # On white pawn
        assert not self.wqueen.can_move(5, 7)  # Behind white pawn
        assert not self.wqueen.can_move(5, 1)  # Behind black pawn

        # Black queen
        assert not self.bqueen.can_move(2, 2)  # On black pawn
        assert not self.bqueen.can_move(1, 1)  # Behind black pawn
        assert not self.bqueen.can_move(1, 7)  # Behind white pawn

    def test_check_pin(self):
        # Check if illegal moves are prevented
        assert not self.pin_wqueen.can_move(1, 5)
        assert not self.pin_bqueen.can_move(6, 3)

    def test_take(self):
        assert self.wqueen.can_move(4, 2)  # Takes black pawn
        assert self.bqueen.can_move(2, 4)  # Takes white queen

    def test_not_on_board(self):
        self.board.remove_piece(2, 4)  # self.wqueen
        assert not self.wqueen.can_move(2, 3)

    def test_invalid_square(self):
        assert not self.wqueen.can_move(3, 2)
        assert not self.wqueen.can_move(-1, 7)
        assert not self.bqueen.can_move(0, 8)
