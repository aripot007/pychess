from pychess.board import Board


class TestRookMoves:

    def setup_method(self):
        self.board = Board.from_fen("r3kn1r/4P3/6P1/8/8/6p1/4p3/R3KN1R w KQkq - 0 1")
        self.wk = self.board.white.king
        self.bk = self.board.black.king

    def teardown_method(self):
        self.board = None

    def test_normal_moves(self):
        # White king
        assert self.wk.can_move(1, 3)
        assert self.wk.can_move(1, 4)  # Take black pawn

        # Black king
        assert self.bk.can_move(6, 3)
        assert self.bk.can_move(6, 4)  # Take white pawn

    def test_move_blocked(self):
        # White king
        assert not self.wk.can_move(0, 5)

        # Black king
        assert not self.bk.can_move(7, 5)

    def test_illegal(self):
        # Check if illegal moves are prevented
        assert not self.wk.can_move(1, 5)
        assert not self.bk.can_move(6, 5)

    def test_take(self):
        assert self.wk.can_move(1, 4)  # Take black pawn
        assert self.bk.can_move(6, 4)  # Take white pawn

    def test_not_on_board(self):
        self.board.remove_piece(0, 4)
        assert not self.wk.can_move(0, 3)

    def test_invalid_square(self):
        assert not self.wk.can_move(-1, 4)
        assert not self.bk.can_move(8, 4)

    def test_get_possible_moves(self):
        # White king
        assert set(self.wk.get_possible_moves()) == {(1, 3), (1, 4)}

        # Black king
        assert set(self.bk.get_possible_moves()) == {(6, 3), (6, 4)}

    def test_castling(self):
        assert not self.wk.can_move(0, 6), "The white king should not be able to castle because the path is blocked by a knight"  # White king side
        assert not self.wk.can_move(0, 2), "The white king should not be able to castle because the path is attacked by a pawn"  # White queen side (blocked by pawn on e1)

        assert not self.bk.can_move(7, 6), "The black king should not be able to castle because the path is blocked by a knight"  # Black king side
        assert not self.bk.can_move(7, 2), "The black king should not be able to castle because the path is attacked by a pawn"  # Black queen side (blocked by pawn on e7)

        # Remove the pawns blocking castling
        self.board.remove_piece(1, 4)
        self.board.remove_piece(6, 4)

        rook = self.board.get_cell(0, 0)
        assert self.wk.can_move(0, 2) and self.bk.can_move(7, 2), "The kings should be able to castle once the attacking pawns have been removed "
        self.wk.move(0, 2)  # White castle queen side
        assert self.board.get_cell(0, 0) is None, "The king should move the rook when castling"
        assert self.board.get_cell(0, 3) == rook, "The king should move the rook when castling"
        assert rook.row == 0 and rook.col == 3, "The rook coordinates should be updated when castling"
        assert self.board.get_cell(0, 2) == self.wk, "The king should move when castling"

    def test_castling_blocked_when_check(self):
        board = Board.from_fen("r3k2r/8/8/1B6/1b6/8/8/R3K2R w KQkq - 0 1")
        wk = board.white.king
        bk = board.black.king

        assert not wk.can_move(0, 2) and not wk.can_move(0, 6), "The white king should not be able to castle when checked"
        assert not bk.can_move(7, 2) and not wk.can_move(7, 6), "The black king should not be able to castle when checked"

