# Faisal Mashhadi
# fmashhad
from ChessEngine import GameLogic
import random

class basicAI():

    def __init__(self, engine, myColor):
        self.Engine = engine
        self.boardState = self.Engine.getBoard()
        self.myColor = myColor


    def getRandomMove(self):
        allMoves, other = self.Engine.getAllPossibleMoves()
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
            return 1 * adjust

        if piece[1] == 'N':
            return 3 * adjust

        if piece[1] == 'B':
            return 3.15 * adjust

        if piece[1] == 'R':
            return 5 * adjust

        if piece[1] == 'Q':
            return 9 * adjust

        else:
            return 0


    def getScore(self, board, currColor):
        score = 0

        # Award points depending on available pieces on the board
        for r in range(8):
            for c in range(8):
                if board[r][c]:
                    score += self.getPieceScore(board[r][c], currColor)


        # Also Award 1.5 point for each check
        checks, pins = self.Engine.checks()
        
        for check in checks:
            score += 1.5


        # Also Award 0.75 points for castling
        whiteKing, blackKing = self.Engine.getKingPositions()
        
        if currColor == 'w':
            kingColor = whiteKing
            r, n, pawn = 7, 5, -1
        else:
            kingColor = blackKing
            r, n, pawn = 0, 2, 1

        if [r,2] in kingColor or [r, 6] in kingColor:
            score += 0.75

        # Also Award points for development
        if board[r][1] and board[r][1][1] != 'N':
            score += .15
        if board[r][6] and board[r][6][1] != 'N':
            score += .15
        if board[r][3] and board[r][3][1] != 'P':
            score += .15
        if board[r][4] and board[r][4][1] != 'P':
            score += .15
        if board[r][2] and board[r][2][1] != 'B':
            score += .1
        if board[r][4] and board[r][4][1] != 'B':
            score += .1
        if board[n][2] and board[n][2][1] == 'N':
            score += .1
        if board[n][5] and board[n][5][1] == 'N':
            score += .1

        # Also Award Points for Pawn Development
        for i in range(8):
            if board[r+2*pawn][i] and board[r+2*pawn][i][1] == 'P':
                if i == 0 or i == 7:
                    score += .2
        if board[4][4] == 'wP':
            if board[3][4] == 'bP':
                score += .3
            score += .2
        if board[4][3] == 'wP':
            if board[3][3] == 'bP':
                score += .3
            score += .2

        return score
    

    def getSmartMove(self, depth=1):
        if depth == 0:
            return 0
        else:
            allMoves, other = self.Engine.getAllPossibleMoves()
            allPieces = list(allMoves.items())

            board = self.boardState
            bestScore = [-100, []]

            for piece in allPieces:
                for move in piece[1:][0]:
                    whatPiece = piece[0]
                    self.Engine.makeMove(whatPiece, move)
                    #self.Engine.switchPlayer()
                    plr = self.Engine.getPlayer()
                    self.boardState = self.Engine.getBoard()

                    #opponentsScore = self.getSmartMove(depth-1)
                    #if not isinstance(opponentsScore, int):
                        #opponentsScore = opponentsScore[0]

                    thisScore = self.getScore(self.boardState, plr) #- opponentsScore
                    self.Engine.undoMove()

                    if thisScore > bestScore[0]:
                        bestScore = [thisScore, [whatPiece, move]]

            if depth == 1:
                if self.Engine.getPlayer() != self.myColor:
                    self.Engine.switchPlayer()
            return bestScore
                    
                
                
                
        

        

