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
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []





#Takes a Move as a parameter and executess it(this will not work for castling, pawn promotion, and en-passannt
    def makeMove(self, move):
        self.board[move.startRow][move.startCol]= "--"
        self.board[move.endRow][move.endCol]= move.pieceMoved
        self.moveLog.append(move)#log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        # update the kings location if moved
        if move.pieceMoved == 'King_W':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'King_B':
            self.blackKingLocation = (move.endRow, move.endCol)

#undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol]= move.pieceMoved
            self.board[move.endRow][move.endCol]= move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back
            if move.pieceMoved == 'King_W':
                self.whiteKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == 'King_B':
                self.blackKingLocation = (move.endRow, move.endCol)


    #all moves considering checks
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndCheck()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check you must move a piece into one of the square between the enemy piece and king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that piece can move to
                #if knight, must capture knight or move king, other pieces van be blocked
                if pieceChecking == 'N':
                    velidSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)#check 2 and check3 are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to piece end checks
                           break

                    #get rid of any moves thar dont block check or move king
                for i in range(len(moves) -1, -1, -1):  #go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'k': #move doesnt move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesnt block check or capture piece
        return moves

    #determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    #determine if the enemey can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponents turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppMoves:
            if move.endRow == r or move.endCol >= c: #square it undder attack
                return True
        return False


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
            if self.board[r + 1][c] == "--":  #1 square move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--": # 2 square moves
                    moves.append(Move((r, c), (r + 2, c), self.board))
            #captures
            if c - 1 >= 0: #captures to left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  #capture to right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
        #add pawn promotions later

    # get all the Rook moves for the rook located at row, col and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemycolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemycolor: #enemy space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #friendly piece invalid
                        break
                else: #off board
                    break

    # get all the Knight moves for the knight located at row, col and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allycolor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece != allycolor: #not an ally piece(empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # get all the Bishop moves for the bishop located at row, col and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemycolor = "b" if self.whiteToMove else "w"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--": #epmty space valid
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                elif endPiece[0] == enemycolor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                    break
                else:
                    break
            else:
                break

    # get all the Queen moves for the queen located at row, col and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # get all the King moves for the King located at row, col and add these moves to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allycolor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allycolor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))




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