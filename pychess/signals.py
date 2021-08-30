from blinker import Signal

# Pieces
PIECE_MOVE = Signal("piece.move")
"""
Emitted after each `Piece.move()`.

*Args:*

- **sender :** The piece moved.

- **start :** A tuple containing the coordinates (row, col) of the square where the piece was.

- **dest :** A tuple containing the coordinates (row, col) of the square where the piece moved.
"""

PIECE_TAKEN = Signal("piece.taken")
"""
Emitted when a piece is taken, after each `Piece.on_eat()`.

*Args :*

- **sender :** The piece getting taken.

- **attacker :** The attacking piece.
"""

# Pawn promotion
PAWN_PROMOTION = Signal("pawn.promotion")
"""
Emitted when a pawn reached the opposite side of the board and is waiting for a promotion.

*Args :*

- **sender :** The pawn waiting for the promotion.
"""

PAWN_PROMOTED = Signal("pawn.promoted")
"""
Emitted when a pawn is promoted, after `Pawn.promote()`.

*Args :*

- **sender :** The pawn that got promoted.

- **piece_type :** The type of piece the pawn was promoted to.
"""

