class GameState:
    def __init__(self):
        self.board = [
            ["Rook_B", "Knight_B", "Bishop_B", "Queen_B", "King_B", "Bishop_B", "Knight_B", "Rook_B"],
            ["Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W"],
            ["Rook_W", "Knight_W", "Bishop_W", "Queen_W", "King_W", "Bishop_W", "Knight_W", "Rook_W"]]
        self.whiteToMove = True
        self.movelog = []
