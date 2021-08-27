from pychess.board import Board


class TestPawnMoves:

    def setup_method(self):
        self.board = Board.from_fen("2k5/Ppppp3/B1P2p1p/4PPP1/1pp4b/3p4/PP1PPP1p/4K3 w - - 0 1")

    def teardown_method(self):
        self.board = None

    def test_can_move_1(self):
        # White king's pawn
        assert self.board.get_cell(1, 4).can_move(2, 4)
        # Black king's pawn
        assert self.board.get_cell(6, 4).can_move(5, 4)

        # Black b6
        assert self.board.get_cell(3, 1).can_move(2, 1)
        # white e6
        assert self.board.get_cell(4, 4).can_move(5, 4)

    def test_move_1_blocked(self):
        # white f6
        assert not self.board.get_cell(4, 5).can_move(5, 5)
        # black f5
        assert not self.board.get_cell(5, 5).can_move(4, 5)

    def test_can_move_2(self):
        # white e4
        assert self.board.get_cell(1, 4).can_move(3, 4)
        # black d5
        assert self.board.get_cell(6, 3).can_move(4, 3)

        # Already moved
        # white g7
        assert not self.board.get_cell(4, 6).can_move(6, 6)
        # black c2
        assert not self.board.get_cell(3, 2).can_move(1, 2)

    def test_move_2_blocked(self):
        # Blocked 2 squares ahead
        # white b4
        assert not self.board.get_cell(1, 1).can_move(3, 1)
        # black e5
        assert not self.board.get_cell(6, 4).can_move(4, 4)

        # Blocked 1 squares ahead
        # white d4
        assert not self.board.get_cell(1, 3).can_move(3, 3)
        # black c5
        assert not self.board.get_cell(6, 2).can_move(4, 2)

    def test_too_far(self):
        # white g5 to g8
        assert not self.board.get_cell(4, 6).can_move(8, 6)
        # black c4 to c1
        assert not self.board.get_cell(3, 2).can_move(0, 2)

    def test_check_pin(self):
        # Check if illegal moves are prevented
        # white f3
        assert not self.board.get_cell(1, 5).can_move(2, 5)
        # black b6
        assert not self.board.get_cell(6, 1).can_move(5, 1)

    def test_take(self):
        p1 = self.board.get_cell(4, 6)
        assert p1.can_move(5, 5)
        assert p1.can_move(5, 7)

        p2 = self.board.get_cell(5, 5)
        assert p2.can_move(4, 6)
        assert p2.can_move(4, 4)

        # Cannot take
        assert not self.board.get_cell(1, 0).can_move(2, 1)
        assert not self.board.get_cell(6, 3).can_move(5, 4)

    def test_en_passant(self):
        self.board.en_passant = (2, 0)
        assert self.board.get_cell(3, 1).can_move(2, 0)

        self.board.en_passant = (5, 3)
        assert self.board.get_cell(4, 4).can_move(5, 3)

    def test_not_on_board(self):
        # White pawn
        piece = self.board.get_cell(1, 1)
        self.board.remove_piece(1, 1)
        assert not piece.can_move(2, 1)
