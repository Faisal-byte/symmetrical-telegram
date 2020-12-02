# Faisal Mashhadi
# fmashhad

# This file handles making intelligent moves by implementing
# a minimax algorithm with alpha beta pruning

from ChessEngine import GameLogic
import random

class basicAI():

    def __init__(self, myColor):
        self.myColor = myColor
        self.Engine = GameLogic()
        self.boardState = self.Engine.getBoard()


    def loadMoves(self, myMoveLog):
        self.Engine.setPlayer(0)
        self.Engine.moveLog.clear()
        self.Engine.resetBoard()

        for move in myMoveLog:
            if type(move) != list:
                self.Engine.makeMove([move.currPos[0], move.currPos[1]],
                                         [move.toPos[0], move.toPos[1]])
                if move.piece == 'wK':
                    king, col, plr = self.Engine.whiteKing, 7, 'w'
                    king.append([move.toPos[0], move.toPos[1]])
                elif move.piece == 'bK':
                    king, col, plr = self.Engine.blackKing, 0, 'b'
                    king.append([move.toPos[0], move.toPos[1]])

                if move.piece[1] == 'K' and len(king) == 2 and king[0] == [col, 4]:
                    if move.toPos[1] == 6:
                        self.Engine.board[col][7] = ''
                        self.Engine.board[col][5] = plr+'Rk'
                        self.movedRooks.append(plr+'Rk')
                    elif move.toPos[1] == 2:
                        self.Engine.board[col][0] = ''
                        self.Engine.board[col][3] = plr+'Rq'
                        self.Engine.movedRooks.append(plr+'Rq')

                self.Engine.switchPlayer()

            else:
                self.Engine.setBoard([move[1][0], move[1][1]], '')
                self.Engine.setBoard([move[1][2], move[1][3]], move[2])
                self.Engine.switchPlayer()


    def undo(self):
        self.Engine.undoMove()
        
    '''
    IMPORTED TABLES BELOW
    '''
    def getPieceTable(self, piece, pos, plr):
        if piece == 'P':
            pawntable = [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, -20, -20, 10, 10, 5,
                5, -5, -10, 0, 0, -10, -5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, 5, 10, 25, 25, 10, 5, 5,
                10, 10, 20, 30, 30, 20, 10, 10,
                50, 50, 50, 50, 50, 50, 50, 50,
                70, 70, 70, 70, 70, 70, 70, 70]

            if plr == 'w':
                pawntable = pawntable[::-1]

            return pawntable[pos[0]*8 + pos[1]]

        if piece == 'N':
            knightstable = [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50]
            if plr == 'w':
                knightstable = knightstable[::-1]

            return knightstable[pos[0]*8 + pos[1]]

        if piece == 'B':
            bishopstable = [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -10, -10, -10, -10, -20]
            if plr == 'w':
                bishopstable = bishopstable[::-1]
            return bishopstable[pos[0]*8 + pos[1]]

        if piece == 'R':
            rookstable = [
                0, 0, 0, 5, 5, 0, 0, 0,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                5, 10, 10, 10, 10, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0]
            if plr == 'w':
                rookstable = rookstable[::-1]
            return rookstable[pos[0]*8 + pos[1]]

        if piece == 'Q':
            queenstable = [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 5, 5, 5, 5, 5, 0, -10,
                0, 0, 5, 5, 5, 5, 0, -5,
                -5, 0, 5, 5, 5, 5, 0, -5,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20]
            if plr == 'w':
                queenstable = queenstable[::-1]
            return queenstable[pos[0]*8 + pos[1]]

        if piece == 'K':
            kingstable = [
                20, 30, 10, 0, 0, 10, 30, 20,
                20, 20, 0, 0, 0, 0, 20, 20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30]
            if plr == 'w':
                kingstable = kingstable[::-1]

            return kingstable[pos[0]*8 + pos[1]]

    '''
    END OF IMPORTED TABLES
    SOURCE: https://medium.com/dscvitpune/lets-create-a-chess-ai-8542a12afef
    '''

    def getRandomMove(self):
        if self.Engine.getPlayer() != self.myColor:
            self.Engine.switchPlayer()
        allMoves, other = self.Engine.getAllPossibleMoves(allMoves=False)
        allPieces = list(allMoves.items())
        piece = random.choice(allPieces) # piece's board pos
        if len(piece[1]) > 1:
            # one of piece's move's
            m = piece[1][random.randint(0, len(piece)-1)] 
        else:
            m = piece[1][0]
        return list(piece[0]), m


    def getPieceScore(self, piece, currColor):
        adjust = 1
        if piece[0] != currColor:
            adjust = -1

        if piece[1] == 'P':
            return 100 * adjust

        if piece[1] == 'N':
            return 300 * adjust

        if piece[1] == 'B':
            return 315 * adjust

        if piece[1] == 'R':
            return 500 * adjust

        if piece[1] == 'Q':
            return 900 * adjust

        else:
            return 0


    def getScore(self, board, currColor=''):

        if currColor == '':
            currColor = self.myColor
        score = 0

        # Award points depending on available pieces on the board
        for r in range(8):
            for c in range(8):
                if board[r][c]:
                    score += self.getPieceScore(board[r][c], currColor)
                    # Also Award points for development
                    if currColor == self.myColor:
                        pointScore = self.getPieceTable(board[r][c][1], [r,c], currColor)
                        score += pointScore

        
        # Also Award 8 point for each check
        checks, pins = self.Engine.checks()
        
        for check in checks:
            score += 8


        # Also Award 90 points for castling
        whiteKing, blackKing = self.Engine.getKingPositions()
        
        if currColor == 'w':
            kingColor = whiteKing
            r, n, adj = 7, 5, -1
        else:
            kingColor = blackKing
            r, n, adj = 0, 2, 1

        if currColor == self.myColor:
            if [r,2] in kingColor or [r, 6] in kingColor:
                score += 90

            # Also Award points for development
            if board[n+adj][4] and board[n+adj][4][1] == 'P':
                score += 75
                if board[n+adj*2][4] and board[n+adj*2][4][1] == 'P':
                    score += 25

            if board[n+adj][3] and board[n+adj][3][1] == 'P':
                score += 75
                if board[n+adj*2][3] and board[n+adj*2][3][1] == 'P':
                    score += 25

            if board[r][2] != 'N':
                score += 5
                if board[n][2] == 'N':
                    score += 20

            if board[r][6] != 'N':
                score += 5
                if board[n][5] == 'N':
                    score += 15

            if board[r][2] != 'B' and board[r][2] != 'R':
                score += 20

            if board[r][5] != 'B' and board[r][5] != 'R':
                score += 20

        return score
    

    def getSmartMove(self, moveLog, board):
        self.loadMoves(moveLog)
        self.Engine.board = board
        
        allMoves, ignore = self.Engine.getAllPossibleMoves(allMoves=False)
        allPieces = list(allMoves.items())

        bestScore = [-1000, []]

        for piece in allPieces:
            for move in piece[1:][0]:
                whatPiece = piece[0]
                self.Engine.makeMove(whatPiece, move)
                self.boardState = self.Engine.getBoard()

                thisScore = self.getScore(self.boardState)
                
                bestEnemyScore = self.minimax(ismax=False)
                    
                overallScore = thisScore + bestEnemyScore

                if overallScore > bestScore[0]:
                    bestScore[0] = overallScore
                    bestScore[1] = [whatPiece, move]

                self.Engine.undoMove()

        return bestScore


    def minimax(self, depth=2, ismax=False, alpha=-100000, beta= 100000):
        if depth == 0:
            return self.getScore(self.boardState)

        if ismax:
            if self.Engine.getPlayer() != self.myColor:
                self.Engine.switchPlayer()

            plr = self.Engine.getPlayer()
            bestScore = -100000

            allMoves, other = self.Engine.getAllPossibleMoves(allMoves=False)
            allPieces = list(allMoves.items())

            for piece in allPieces:
                for move in piece[1:][0]:
    
                    whatPiece = piece[0]
                    self.Engine.makeMove(whatPiece, move)
                    self.boardState = self.Engine.getBoard()
                    myScore = self.getScore(self.boardState, plr)
                    bestEnemyScore = self.minimax(depth-1, not ismax, alpha, beta)
                    overallScore = myScore + bestEnemyScore

                    self.Engine.undoMove()

                    if overallScore > bestScore:
                        alpha = overallScore
                        bestScore = overallScore

                    if beta <= alpha:
                        return bestScore

            return bestScore

        else:
            if self.Engine.getPlayer() == self.myColor:
                self.Engine.switchPlayer()

            plr = self.Engine.getPlayer()
            bestScore = 100000

            allMoves, other = self.Engine.getAllPossibleMoves()
            allPieces = list(allMoves.items())

            for piece in allPieces:
                for move in piece[1:][0]:
                    
                    whatPiece = piece[0]
                    self.Engine.makeMove(whatPiece, move)
                    self.boardState = self.Engine.getBoard()
                    myScore = -self.getScore(self.boardState, plr)
                    bestEnemyScore = self.minimax(depth-1, not ismax, alpha, beta)
                    overallScore = myScore + bestEnemyScore

                    self.Engine.undoMove()

                    if overallScore < bestScore:
                        beta = overallScore
                        bestScore = overallScore 

                    if beta <= alpha:
                        return bestScore

            return bestScore
                

                            
