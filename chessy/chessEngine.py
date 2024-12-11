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

    def makeMove(self, move):
        self.board[move.startRow][move.startCol]= "--"
        self.board[move.endRow][move.endCol]= move.pieceMoved
        self.movelog.append(move)#log the move so we can undo it later
        self.magentaToMove = not self.magentaToMove #swap players

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}



    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


