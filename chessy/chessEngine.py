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
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKnightMoves}
        self.whiteToMove = True
        self.movelog = []


#Takes a Move as a parameter and executess it(this will not work for castling, pawn promotion, and en-passannt
    def makeMove(self, move):
        self.board[move.startRow][move.startCol]= "--"
        self.board[move.endRow][move.endCol]= move.pieceMoved
        self.movelog.append(move)#log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players

#undo the last move made
    def undoMove(self):
        if len(self.movelog) != 0: #make sure that there is a move to undo
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol]= move.pieceMoved
            self.board[move.endRow][move.endCol]= move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back

    #all moves considering checks
    def getValidMoves(self):
        return self.getAllPossibleMoves() #for now will not worry about checks

    #all moves without considering checks
    def getAllPossibleMoves(self):
        moves = [Move((6,4), (4, 4), self.board)]
        for r  in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function based on piece type
        return moves

    # get all the pawn moves for the pawn located at row, col and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else: #black pawn moves
            if self.board[r+1][c] == "--":  #1 square move
                moves.append(Move((r, c), (r + 1, c), self.board))

    # get all the Rook moves for the rook located at row, col and add these moves to the list
    def getRookMoves(self, r, c, moves):
        pass

    # get all the Knight moves for the knight located at row, col and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        pass

    # get all the Bishop moves for the bishop located at row, col and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        pass

    # get all the Queen moves for the queen located at row, col and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        pass

    # get all the King moves for the King located at row, col and add these moves to the list
    def getKingMoves(self, r, c, moves):
        pass




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
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol



#overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


