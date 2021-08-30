from pychess.board import Board


class TestBishopMoves:

    def setup_method(self):
        self.board = Board.from_fen("4k3/1pp2b1r/8/4b2B/4B3/8/1PP5/7K w - - 0 1")

    def teardown_method(self):
        self.board = None

    def test_can_move_diagonal(self):
        # White bishop on e4
        bishop = self.board.get_cell(3, 4)
        assert bishop.can_move(5, 6)  # Up right
        assert bishop.can_move(5, 2)  # Up left
        assert bishop.can_move(2, 3)  # Down left
        assert bishop.can_move(1, 6)  # Down right

        # Black bishop on e5
        bishop = self.board.get_cell(4, 4)
        assert bishop.can_move(7, 7)  # Up right
        assert bishop.can_move(5, 3)  # Up left
        assert bishop.can_move(2, 2)  # Down left
        assert bishop.can_move(1, 7)  # Down right

    def test_move_blocked(self):
        # White bishop on e4
        bishop = self.board.get_cell(3, 4)
        assert not bishop.can_move(1, 2)  # On white pawn
        assert not bishop.can_move(0, 1)  # Behind white pawn
        assert not bishop.can_move(7, 0)  # Behind black pawn

        # Black bishop on e5
        bishop = self.board.get_cell(4, 4)
        assert not bishop.can_move(6, 2)  # On black pawn
        assert not bishop.can_move(7, 1)  # Behind black pawn
        assert not bishop.can_move(0, 0)  # Behind white pawn

    def test_check_pin(self):
        # Check if illegal moves are prevented
        assert not self.board.get_cell(4, 7).can_move(1, 4)
        assert not self.board.get_cell(6, 5).can_move(1, 0)

    def test_take(self):
        assert self.board.get_cell(3, 4).can_move(6, 7)  # Takes black rook
        assert self.board.get_cell(4, 4).can_move(1, 1)  # Takes white pawn

    def test_not_on_board(self):
        piece = self.board.get_cell(3, 4)
        self.board.remove_piece(3, 4)
        assert not piece.can_move(4, 5)

    def test_invalid_square(self):
        bishop = self.board.get_cell(6, 5)
        assert not bishop.can_move(5, 5)
        assert not bishop.can_move(8, 7)
        assert not bishop.can_move(0, -1)

    def test_get_possible_moves(self):
        # White bishop on e4
        bishop = self.board.get_cell(3, 4)
        assert set(bishop.get_possible_moves()) == {(4, 3), (6, 1), (2, 3), (6, 7), (4, 5), (5, 6), (1, 6), (2, 5), (5, 2)}

        # Black bishop on e5
        bishop = self.board.get_cell(4, 4)
        assert set(bishop.get_possible_moves()) == {(5, 5), (7, 7), (1, 1), (5, 3), (1, 7), (3, 3), (2, 6), (2, 2), (6, 6), (3, 5)}
