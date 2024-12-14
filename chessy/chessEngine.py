class GameState:
    def __init__(self):
        self.board = self.createBoard()
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []

    def createBoard(self):
        # Tahtayı oluştur, başlangıç durumundaki taşlar yerleştirilecek.
        board = [
            ["Rook_B", "Knight_B", "Bishop_B", "Queen_B", "King_B", "Bishop_B", "Knight_B", "Rook_B"],
            ["Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B", "Pawn_B"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W", "Pawn_W"],
            ["Rook_W", "Knight_W", "Bishop_W", "Queen_W", "King_W", "Bishop_W", "Knight_W", "Rook_W"]
        ]
        return board

    def getValidMoves(self):
        self.inCheck, self.pins, self.checks = self.checkForPinsAndCheck()
        validMoves = []
        # Burada geçerli hamleleri döndürebilirsiniz
        return validMoves

    def checkForPinsAndCheck(self):
        pins = []
        checks = []
        inCheck = False

        # Kontrol edilecek oyuncu
        if self.whiteToMove:
            kingLocation = self.whiteKingLocation
        else:
            kingLocation = self.blackKingLocation

        # Diğer oyuncunun taşlarını kontrol et
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '--':  # Eğer bir taş varsa
                    if self.whiteToMove and piece.endswith("_B"):  # Siyah taşlar
                        # Burada, siyah taşların beyaz şahına tehdit oluşturup oluşturmadığını kontrol edebilirsiniz
                        pass
                    elif not self.whiteToMove and piece.endswith("_W"):  # Beyaz taşlar
                        # Burada, beyaz taşların siyah şahına tehdit oluşturup oluşturmadığını kontrol edebilirsiniz
                        pass

        return inCheck, pins, checks

    def makeMove(self, move):
        # Bu fonksiyon, bir hamleyi geçerli yapar
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

    def undoMove(self):
        if self.moveLog:
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured

class Move:
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getChessNotation(self):
        return f"{self.pieceMoved} from ({self.startRow}, {self.startCol}) to ({self.endRow}, {self.endCol})"
