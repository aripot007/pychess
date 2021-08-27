from pychess.pieces import *
from pychess.player import *


class TestSAN:

    def setup_class(self):
        self.white_player = Player(COLOR_WHITE, "White Player")
        self.black_player = Player(COLOR_BLACK, "Black Player")

    def teardown_method(self):
        self.white_player.pieces = []
        self.black_player.pieces = []

    def test_pawn_san(self):
        p1 = Pawn(self.white_player)
        p2 = Pawn(self.black_player)

        assert p1.san == "P"
        assert p2.san == "p"

    def test_knight_san(self):
        p1 = Knight(self.white_player)
        p2 = Knight(self.black_player)

        assert p1.san == "N"
        assert p2.san == "n"

    def test_bishop_san(self):
        p1 = Bishop(self.white_player)
        p2 = Bishop(self.black_player)

        assert p1.san == "B"
        assert p2.san == "b"

    def test_rook_san(self):
        p1 = Rook(self.white_player)
        p2 = Rook(self.black_player)

        assert p1.san == "R"
        assert p2.san == "r"

    def test_queen_san(self):
        p1 = Queen(self.white_player)
        p2 = Queen(self.black_player)

        assert p1.san == "Q"
        assert p2.san == "q"

    def test_king_san(self):
        p1 = King(self.white_player)
        p2 = King(self.black_player)

        assert p1.san == "K"
        assert p2.san == "k"