import types

from pychess.board import Board
import pychess.pieces as pieces
import pychess.signals as signals


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
        self.board.get_cell(1, 0).move(3, 0)  # Move the white pawn to a4
        self.board.en_passant = (2, 0)  # We do not test if the en_passant field is set correctly, as this is the board's responsability
        assert self.board.get_cell(3, 1).can_move(2, 0), "The white pawn should be able to move to the board's en passant square"
        self.board.get_cell(3, 1).move(2, 0)  # Take
        assert self.board.get_cell(3, 0) is None, "The white pawn taking en passant should ensure the opponent's pawn is taken"

        self.board.get_cell(6, 3).move(4, 3)  # Move the black pawn to d5
        self.board.en_passant = (5, 3)
        assert self.board.get_cell(4, 4).can_move(5, 3), "The black pawn should be able to move to the board's en passant square"
        self.board.get_cell(4, 4).move(5, 3)  # Take
        assert self.board.get_cell(4, 3) is None, "The black pawn taking en passant should ensure the opponent's pawn is taken"

    def test_not_on_board(self):
        # White pawn
        piece = self.board.get_cell(1, 1)
        self.board.remove_piece(1, 1)
        assert not piece.can_move(2, 1)

    def test_get_possible_moves(self):
        # White pawn on e2
        pawn = self.board.get_cell(1, 4)
        assert set(pawn.get_possible_moves()) == {(2, 4), (3, 4), (2, 3)}

        # Black pawn on d7
        pawn = self.board.get_cell(6, 3)
        assert set(pawn.get_possible_moves()) == {(5, 3), (5, 2), (4, 3)}

        # Test en passant (black pawn on b4)
        pawn = self.board.get_cell(3, 1)
        self.board.en_passant = (2, 0)
        assert set(pawn.get_possible_moves()) == {(2, 0), (2, 1)}

        # Test blocked pawn (white pawn on f5)
        pawn = self.board.get_cell(4, 5)
        assert pawn.get_possible_moves() == []

    def test_promote_signals(self):
        """
        Test if the pawn emits a signal when asking for a promotion and when promoted
        """
        # TODO: Mock functions that asks for promotion
        promotion_signals = []
        promoted_signals = []

        @signals.PAWN_PROMOTION.connect
        def on_promotion(sender, **kwargs):
            nonlocal promotion_signals
            promotion_signals.append((sender, kwargs))

        @signals.PAWN_PROMOTED.connect
        def on_promoted(sender, **kwargs):
            nonlocal promoted_signals
            promoted_signals.append((sender, kwargs))

        # White pawn
        assert len(promotion_signals) == 0 and len(promoted_signals) == 0, "Signals counts should be 0 when starting this test"
        pawn = self.board.get_cell(6, 0)
        pawn.move(7, 0)
        assert len(promotion_signals) == 1, "The PAWN_PROMOTION signal should be sent when a white pawn is ready for promotion"
        assert promotion_signals[-1] == (pawn, {}), "The PAWN_PROMOTION sender should be the piece to promote, and there shouldn't be any kwargs"
        pawn.promote(pieces.Bishop)
        assert len(promoted_signals) == 1, "The PAWN_PROMOTED signal should be sent when a white pawn is promoted"
        assert promoted_signals[-1] == (pawn, {"piece_type": pieces.Bishop}),\
            "The PAWN_PROMOTED sender should be the piece promoted, and the type to promote to should be specified as piece_type"

        # Black pawn
        pawn = self.board.get_cell(1, 7)
        pawn.move(0, 7)
        assert len(promotion_signals) == 2, "The PAWN_PROMOTION signal should be sent when a black pawn is ready for promotion"
        assert promotion_signals[-1] == (pawn, {}),\
            "The PAWN_PROMOTION sender should be the piece to promote, and there shouldn't be any kwargs"
        pawn.promote(pieces.Queen)
        assert len(promoted_signals) == 2, "The PAWN_PROMOTED signal should be sent when a black pawn is promoted"
        assert promoted_signals[-1] == (pawn, {"piece_type": pieces.Queen}),\
            "The PAWN_PROMOTED sender should be the piece promoted, and the type to promote to should be specified as piece_type"

    def test_promote(self):
        """
        Test if the pawn promotion overrides the movement and the display methods correctly
        """
        pawn = self.board.get_cell(6, 0)
        pawn.promote(pieces.Rook)

        assert pawn.move == types.MethodType(pieces.Rook.move, pawn), "The promotion should override the move method"
        assert pawn.can_move == types.MethodType(pieces.Rook.can_move, pawn), "The promotion should override the can_move method"
        assert pawn.get_possible_moves == types.MethodType(pieces.Rook.get_possible_moves, pawn), "The promotion should override the get_possible_moves method"
        assert pawn.icon == types.MethodType(pieces.Rook.icon, pawn), "The promotion should override the icon method"
        assert pawn.display == types.MethodType(pieces.Rook.display, pawn), "The promotion should override the display method"
        assert pawn.value == pieces.Rook.VALUE, "The promotion should override the value propertie"
