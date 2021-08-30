from pychess.board import Board


class TestKnightMoves:

    def setup_method(self):
        self.board = Board.from_fen("4k3/5n2/8/2n4B/p3P2b/2N5/5N2/4K3 w - - 0 1")
        self.wn = self.board.get_cell(2, 2)  # White knight
        self.bn = self.board.get_cell(4, 2)  # Black knight

    def teardown_method(self):
        self.board = None

    def test_normal_move(self):
        # White knight
        assert self.wn.can_move(4, 1)
        assert self.wn.can_move(4, 3)
        assert self.wn.can_move(1, 0)
        assert self.wn.can_move(1, 4)
        assert self.wn.can_move(0, 1)
        assert self.wn.can_move(0, 3)

        # Black knight
        assert self.bn.can_move(2, 1)
        assert self.bn.can_move(2, 3)
        assert self.bn.can_move(5, 0)
        assert self.bn.can_move(5, 4)
        assert self.bn.can_move(6, 1)
        assert self.bn.can_move(6, 3)

    def test_move_blocked(self):
        assert not self.wn.can_move(3, 4)  # Blocked by white pawn
        assert not self.bn.can_move(3, 0)  # Blocked by black pawn

    def test_check_pin(self):
        # Check if illegal moves are prevented
        assert not self.board.get_cell(1, 5).can_move(0, 3)
        assert not self.board.get_cell(6, 5).can_move(7, 3)

    def test_take(self):
        assert self.wn.can_move(3, 0)  # Takes black pawn
        assert self.bn.can_move(3, 4)  # Takes white pawn

    def test_not_on_board(self):
        self.board.remove_piece(2, 2)  # White knight on c3
        assert not self.wn.can_move(0, 1)

    def test_invalid_square(self):
        assert not self.wn.can_move(1, 1)
        assert not self.wn.can_move(8, 7)
        assert not self.wn.can_move(0, -1)
