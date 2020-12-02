# Faisal Mashhadi
# fmashhad

# This file is the Engine for implementing all the rules of Chess
# This includes castling and en passant moves :D
from collections import Counter

class GameLogic():
    def __init__(self):
        # This is the core of my project. All rules laws are governed by this
        # tabel :D
        self.board = [
        ['bRq', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bRk'],
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
        ['wRq', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wRk']]

        self.moveLog = []
        self.boardPositionsData = []
        self.player = 0
        self.whiteKing = [[7,4]]
        self.blackKing = [[0,4]]
        self.movedRooks = []
        self.enPassant = []


    def getBoard(self):
        return self.board


    def setBoard(self, pos, title):
        self.board[pos[0]][pos[1]] = title


    def resetBoard(self):
        self.board = [
        ['bRq', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bRk'],
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
        ['wRq', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wRk']]
        

    def setPlayer(self, plr):
        self.player = plr


    def getMoveLog(self):
        return self.moveLog


    def getPlayer(self):
        if self.player % 2 == 0:
            return "w"
        return "b"


    def getKingPositions(self):
        return self.whiteKing, self.blackKing


    def switchPlayer(self):
        self.player += 1


    def clearEnPassant(self):
        self.enPassant = []


    def undoMove(self):
        if len(self.moveLog) >= 1:
            # lMove is the last move done by a player
            lMove = self.moveLog.pop()
            self.board[lMove.currPos[0]][lMove.currPos[1]] = lMove.piece

            if lMove.piece[1] == 'P':
                if lMove.isEnPassant:
                    # THIS PAWN DID AN EN PASSANT
                    if lMove.piece[0] == 'w':
                        self.board[lMove.toPos[0]+1][lMove.toPos[1]] = lMove.capturedPiece
                        self.board[lMove.toPos[0]][lMove.toPos[1]] = ''
                        self.enPassant.append([lMove.toPos[0], lMove.toPos[1]])
                    else:
                        self.board[lMove.toPos[0]-1][lMove.toPos[1]] = lMove.capturedPiece
                        self.board[lMove.toPos[0]][lMove.toPos[1]] = ''
                        self.enPassant.append([lMove.toPos[0], lMove.toPos[1]])

            if len(self.moveLog) > 0:
                tMove = self.moveLog.pop()
                if tMove.piece[1] == 'P':
                    if abs(tMove.currPos[0] - tMove.toPos[0]) > 1:
                        if tMove.piece[0] == 'w':
                            self.enPassant.append([tMove.currPos[0]-1, tMove.currPos[1]])
                        else:
                            self.enPassant.append([tMove.currPos[0]+1, tMove.currPos[1]])
                self.moveLog.append(tMove)
            
            if not lMove.isEnPassant:
                self.board[lMove.toPos[0]][lMove.toPos[1]] = lMove.capturedPiece

            if lMove.piece == 'wK':
                king, col, plr = self.whiteKing, 7, 'w'
                king.pop()

            elif lMove.piece == 'bK':
                king, col, plr = self.blackKing, 0, 'b'
                king.pop()

            if lMove.piece[1] == 'K' and len(king) == 1 and king[0] == [col, 4]:
                if lMove.toPos[1] == 6: 
                    self.board[col][7] = plr+'Rk'
                    self.board[col][5] = ''
                    self.movedRooks.remove(plr+'Rk')

                elif lMove.toPos[1] == 2:
                    self.board[col][0] = plr+'Rq'
                    self.board[col][3] = ''
                    self.movedRooks.remove(plr+'Rq')

            return True



    def makeMove(self, currPos, toPos, board=[]):
        if len(board) == 0:
            board = self.board
        # where currPos and toPos are both lists of [row, column] 
        if self.isValidMove(currPos, toPos) != 'REJECTED':
            self.clearEnPassant()
            self.moveLog.append(Move(self, currPos, toPos))

            piece = board[currPos[0]][currPos[1]]
            capturedPiece = board[toPos[0]][toPos[1]]

            # EN PASSANT
            if piece[1] == 'P':
                if not capturedPiece and currPos[1] != toPos[1]:
                    # THIS PAWN DID AN EN PASSANT
                    if piece[0] == 'w':
                        self.board[toPos[0]+1][toPos[1]] = ''
                    else:
                        self.board[toPos[0]-1][toPos[1]] = ''
            
            board[currPos[0]][currPos[1]] = ''
            board[toPos[0]][toPos[1]] = piece

            if piece == 'wK':
                king, col, plr = self.whiteKing, 7, 'w'
                king.append([toPos[0], toPos[1]])
            elif piece == 'bK':
                king, col, plr = self.blackKing, 0, 'b'
                king.append([toPos[0], toPos[1]])

            if piece[1] == 'K' and len(king) == 2 and king[0] == [col, 4]:
                if toPos[1] == 6:
                    board[col][7] = ''
                    board[col][5] = plr+'Rk'
                    self.movedRooks.append(plr+'Rk')
                elif toPos[1] == 2:
                    board[col][0] = ''
                    board[col][3] = plr+'Rq'
                    self.movedRooks.append(plr+'Rq')

            # PAWN PROMOTION and EN PASSANT
            if piece == 'wP':
                if toPos[0] == 0:
                    return "PROMOTION"
                if currPos[0] == 6 and toPos[0] == 4:
                    # Account for En Passant moves
                    self.enPassant.append([5, currPos[1]])
            
            elif piece == 'bP':
                if toPos[0] == 7:
                    return "PROMOTION"
                if currPos[0] == 1 and toPos[0] == 3:
                    # Account for En Passant moves
                    self.enPassant.append([2, currPos[1]])

            return "SUCCESS"
        return "REJECTED"


    def getValidSquares(self, currPos, board=[]):
        board = self.board
        piece = board[currPos[0]][currPos[1]]
        if piece:
            currPiece = ChessPieces(piece[1], currPos, board, 
                self.whiteKing, self.blackKing, self.movedRooks,
                self.enPassant)
        else:
            return []
        allChecks, pins = self.checks()

        validSquares = currPiece.getPieceMoves()
        checkHolders = []
        newValidSquares = []
        useNewSquares = False

        if allChecks:
            useNewSquares = True

            for checks in allChecks:
                # 'other' is the piece putting the king in check
                # and 'piece' is the current selected piece
                other = board[checks[0]][checks[1]][1]
                otherPiece = ChessPieces(other, [checks[0], checks[1]],
                    board, self.whiteKing, self.blackKing, self.movedRooks,
                    self.enPassant)
                otherPieceSquares = otherPiece.getPieceMoves()
                otherPieceSquares2 = otherPieceSquares[:]

                
                # find which squares the piece can be placed to block 'other'
                if checks[3] == 0:
                    # up and down
                    for square in otherPieceSquares2:
                        if square[1] != checks[1]:
                                otherPieceSquares.remove(square)
                        
                        elif checks[2] == 2 and square[0] > checks[0]:
                            otherPieceSquares.remove(square)
                        
                        elif checks[2] == 1 and square[0] < checks[0]:
                                otherPieceSquares.remove(square)

                if checks[3] == 1:
                    # left and right
                    for square in otherPieceSquares2:
                        if square[0] != checks[0]:
                                otherPieceSquares.remove(square)
                        
                        elif checks[2] == 2 and square[1] > checks[1]:
                            otherPieceSquares.remove(square)
                        
                        elif checks[2] == 1 and square[1] < checks[1]:
                                otherPieceSquares.remove(square)

                if checks[3] == -2:
                    # remove the square in front of pawn, it cannot attack :D
                    for square in otherPieceSquares:
                        if square[1] == checks[1]:
                            otherPieceSquares2.remove(square)

                if piece[1] != 'K':
                    if checks[2] >= 1 and checks[3] >= 2:
                        i, s, s2 = 0, [checks[0], checks[1]], []
                        # diagonals
                        if checks[2] == 1 and checks[3] == 3:
                            j, k = -1, 1
                        if checks[2] == 2 and checks[3] == 3:
                            j, k = -1, -1
                        if checks[2] == 1 and checks[3] == 2:
                            j, k = 1, 1
                        if checks[2] == 2 and checks[3] == 2:
                            j, k = 1, -1
                       
                        while s:
                            if [s[0]+(i*j), s[1]+(i*k)] in validSquares:
                                s2.append([s[0]+(i*j), s[1]+(i*k)])
                            i += 1
                            if not -1 < s[0]+(i*j) < 8 or not -1 < s[1]+(i*k) < 8:
                                s = ''
                    
                        validSquares = s2[:]
                    
                    if checks[3] == -1 or checks[3] == -2:
                        # This is a Knight or Pawn putting the king in check
                        # They cant make pins so just check if this piece can attack
                        for square in validSquares:
                            if square == [checks[0], checks[1]]:
                                newValidSquares.append(square)
                    else:
                        # Just make sure the piece's squares block the check
                        otherPieceSquares.append([checks[0], checks[1]])
                        for square in validSquares:
                            if square in otherPieceSquares:
                                newValidSquares.append(square)
                else:
                    for square in validSquares:
                        if [checks[0], checks[1]] == square:
                            attacking, pins = self.checks([checks[0], checks[1], piece[0]])
                            if len(attacking) == 0:
                                newValidSquares.append(square)

                        
                        if not square in otherPieceSquares2:
                            if checks[3] == 0:
                                # up and down
                                if square[1] != checks[1]:
                                    attacking, pins = self.checks([square[0], square[1], piece[0]])
                                    if len(attacking) == 0:
                                        newValidSquares.append(square)
                            if checks[3] == 1:
                                # left and right
                                if square[0] != checks[0]:
                                    attacking, pins = self.checks([square[0], square[1], piece[0]])
                                    if len(attacking) == 0:
                                        newValidSquares.append(square)

                            if checks[2] >= 1 and checks[3] >= 2:
                                # diagonals
                                s, i = [checks[0], checks[1]], 0
                                
                                if checks[2] == 1 and checks[3] == 2:
                                    j, k = 1, 1
                                if checks[2] == 1 and checks[3] == 3:
                                    j, k = -1, 1
                                if checks[2] == 2 and checks[3] == 2:
                                    j, k = 1, -1
                                if checks[2] == 2 and checks[3] == 3:
                                    j, k = -1, -1
                                
                                append = True
                                
                                while s:
                                    if [s[0]+(i*j), s[1]+(i*k)] == square:
                                        append = False
                                    
                                    i += 1
                                    if not -1 < s[0]+(i*j) < 8 or not -1 < s[1]+(i*k) < 8:
                                        s = ''
                                if append:
                                    attacking, pins = self.checks([square[0], square[1], piece[0]])
                                    if len(attacking) == 0:
                                        newValidSquares.append(square)
                            
                            if checks[3] == -1 or checks[3] == -2:
                                # A pawn or Knight is attacking the king
                                attacking, pins = self.checks([square[0], square[1], piece[0]])
                                if len(attacking) == 0:
                                    newValidSquares.append(square)

                for square in newValidSquares:
                    checkHolders.append(square)
                newValidSquares = []

            for square in validSquares:
                if checkHolders.count(square) >= len(allChecks):
                    newValidSquares.append(square)

            if piece[1] == 'K':
                # make sure to not allow castling when in check
                if [currPos[0], 6] in newValidSquares:
                    newValidSquares.remove([currPos[0], 6])
                if [currPos[0], 2] in newValidSquares:
                    newValidSquares.remove([currPos[0], 2])


        elif piece[1] == 'K':
            useNewSquares = True
            allAttackingSquares = []
            for square in validSquares:  
                attacking, pins = self.checks([square[0], square[1], piece[0]])
                if len(attacking) == 0:
                    newValidSquares.append(square)
                else:
                    allAttackingSquares.append(square)

            # make sure not to allow castling if a piece is attacking a
            # castling square
            if [currPos[0], 5] in allAttackingSquares:
                if [currPos[0], 6] in newValidSquares:
                    newValidSquares.remove([currPos[0], 6])
            if [currPos[0], 3] in allAttackingSquares:
                if [currPos[0], 2] in newValidSquares:
                    newValidSquares.remove([currPos[0], 2])


        

        if pins:
            for pin in pins:
                if currPos == pin[:2]:
                    useNewSquares = True
                    for validSquare in validSquares:
                        if pin[3] == 1:
                            # we can go up or down
                            if validSquare[0] == pin[0]:
                                newValidSquares.append(validSquare)
                        elif pin[3] == 0:
                            # we can go left or right
                            if validSquare[1] == pin[1]:
                                newValidSquares.append(validSquare)

                        elif pin[2] >= 1 and pin[3] >= 2:

                            s, i = pin[4], 0
                            
                            if pin[2] == 1 and pin[3] == 2:
                                j, k = 1, 1

                            if pin[2] == 1 and pin[3] == 3:
                                j, k = -1, 1

                            if pin[2] == 2 and pin[3] == 2:
                                j, k = 1, -1

                            if pin[2] == 2 and pin[3] == 3:
                                j, k = -1, -1

                            while s:
                                if [s[0]+(i*j), s[1]+(i*k)] == validSquare:
                                    newValidSquares.append(validSquare)
                                        
                                i += 1
                                    
                                if not -1 < s[0]+(i*j) < 8 or not -1 < s[1]+(i*k) < 8:
                                    s = ''                

        if not useNewSquares:
            newValidSquares = validSquares

        return newValidSquares


    def isValidMove(self, currPos, toPos, board=[]):
        if toPos in self.getValidSquares(currPos, board):
            return True
        return 'REJECTED'


    def checks(self, pos=[], board=[]):
        if len(board) == 0:
            board = self.board
        temp = []
        attackingPieces = []
        pinnedPieces = []

        if len(pos) == 0:
            if self.player%2 == 0:
                king = self.whiteKing[-1]
                enemy, plr = 'b', -1
            else:
                king = self.blackKing[-1]
                enemy, plr = 'w', 1
        else:
            king, ally = [pos[0], pos[1]], pos[2]
            if ally == 'w':
                enemy, plr = 'b', -1
            else:
                enemy, plr = 'w', 1

        # find all pinned and some attacking pieces (Queen, Rook and Bishop)
        for j in range(4):
            # when j == 0 check for up and down
            # when j == 1 check for left and right

            # when j == 2 check for diagonal up
            # when j == 3 check for diagonal down
            for i in range(1,3):
                # when i == 1 check for left side
                # when i == 2 check for right side
                if j <= 1:
                    pos = [king[0]+(-1+j)**i, king[1]+(-j)**i]
                    enemy1, enemy2 = f"{enemy}Q", f"{enemy}R"
                    temp = []
                else:
                    pos = [king[0]+(-1)**(j-1), king[1]+(-1)**i]
                    enemy1, enemy2 = f"{enemy}Q", f"{enemy}B"
                    temp = []
                
                threat = True
                check = False

                while -1 < pos[0] < 8 and -1 < pos[1] < 8 and threat and not check:
                    square = board[pos[0]][pos[1]]

                    if square:
                        # if this square has a piece, check what piece this is
                        if self.getPlayer() == square[0] and len(temp) == 0:
                            # it is our piece, so it has a potential to be a pin
                            temp.append([pos[0], pos[1]])
                        else:
                            # it is not our piece, so 
                            if square == enemy1 or square[:2] == enemy2:
                                if len(temp) == 0:
                                    # this is a check
                                    attackingPieces.append([pos[0], pos[1], i, j])
                                    check = True
                            
                                elif len(temp) == 1:
                                    # this is a pin
                                    pinnedPieces.append([temp[0][0], temp[0][1], i, j, [pos[0], pos[1]]])
                                    threat = False
                                    temp = []

                            elif len(temp) == 1:
                                # this is an opponent's after our piece that cannot attack
                                # or another of our piece, shich means no checks :D
                                threat = False
                                temp = []
                            else:
                                # this is an opponent's peice that cannot attack
                                threat = False

                    if j < 2:
                        pos = [pos[0]+(-1+j)**i, pos[1]+(-j)**i]     
                    else:
                        pos = [pos[0]+(-1)**(j-1), pos[1]+(-1)**i]


        # find all attacking pieces (king, knights and pawns)
        # Knights
        for j in range(-1, 2, 2):
            for i in range(2):
                pos1 = [king[0]+((-i-1)*j), king[1]+2-i]
                pos2 = [king[0]+((-i-1)*j), king[1]-2+i]

                if -1 < pos1[0] < 8 and -1 < pos1[1] < 8:
                    if board[pos1[0]][pos1[1]] == f"{enemy}N":
                        attackingPieces.append([pos1[0], pos1[1], i-1 , -1])

                if -1 < pos2[0] < 8 and -1 < pos2[1] < 8:
                    if board[pos2[0]][pos2[1]] == f"{enemy}N":
                        attackingPieces.append([pos2[0], pos2[1], i-1, -1])

        # Pawns
        for i in range(-1, 2, 2):
            pos1 = [king[0]+plr, king[1]+i]

            if -1 < pos1[0] < 8 and -1 < pos1[1] < 8:
                if board[pos1[0]][pos1[1]] == f"{enemy}P":
                    attackingPieces.append([pos1[0], pos1[1], i-1, -2])

        # King
        for j in range(-1, 2, 2):
            for i in range(3):
                pos1 = [king[0]-j, king[1]-1+i]

                if -1 < pos1[0] < 8 and -1 < pos1[1] < 8:
                    if board[pos1[0]][pos1[1]] == f"{enemy}K":
                        attackingPieces.append([pos1[0], pos1[1], i-2, -3])

        for i in range(-1, 2, 2):
            pos2 = [king[0], king[1]-i]

            if -1 < pos2[0] < 8 and -1 < pos2[1] < 8:
                if board[pos2[0]][pos2[1]] == f"{enemy}K":
                    attackingPieces.append([pos2[0], pos2[1], i-2, -3])


        return attackingPieces, pinnedPieces


    def getAllPossibleMoves(self, board=[], allMoves=True, AI=False):
        allPieces = []
        allPossibleMoves = {}
        color = self.getPlayer()
        if len(board) == 0:
            board = self.board

        # get allPieces and allPossibleMoves from the board
        for r in range(8):
            for c in range(8):
                if board[r][c]:
                    # if there is a piece, append this piece to allPieces
                    if not allMoves:
                        if board[r][c][1] == color:
                            allPieces.append(board[r][c][1])
                    else:
                        allPieces.append(board[r][c][1])
                    if board[r][c][0] == color:
                        validSquares = self.getValidSquares([r, c])
                        if validSquares:
                            # if there is a valid move, append it to allPossibleMoves
                            allPossibleMoves[r,c] = validSquares

        return allPossibleMoves, allPieces


    def isGameOver(self):
        checks, pins = self.checks()
        allPossibleMoves, allPieces = self.getAllPossibleMoves()

        # if there is a check and the opponent has no possible moves 
        # then this is a checkmate
        if len(allPossibleMoves) == 0 and len(checks) > 0:
            return "CheckMate"

        # else if there are no moves and no checks then this is a stalemate
        elif len(allPossibleMoves) == 0 and len(checks) == 0:
            return "StaleMate"

        # if there is not enough material then it is a draw
        if len(allPieces) == 2 or (len(allPieces) == 3 and (
            ('N' in allPieces) or ('B' in allPieces) )):
            return "Not Enough Material"

        return "Continue"


class Move():
    def __init__(self, game, currPos, toPos):
        self.currPos = currPos
        self.toPos = toPos

        self.piece = game.board[currPos[0]][currPos[1]]
        self.capturedPiece = game.board[toPos[0]][toPos[1]]
        self.isEnPassant = False

        # EN PASSANT
        if self.piece[1] == 'P':
            if not self.capturedPiece and self.currPos[1] != self.toPos[1]:
                # THIS PAWN DID AN EN PASSANT
                if self.piece[0] == 'w':
                    self.capturedPiece = game.board[toPos[0]+1][toPos[1]]
                    self.isEnPassant = True
                else:
                    self.capturedPiece = game.board[toPos[0]-1][toPos[1]]
                    self.isEnPassant = True


class ChessPieces():
    def __init__(self, piece, currPos, board, wKing, bKing, rooks, enPassant):
        self.piece = piece
        self.currSqr = currPos
        self.board = board
        self.color = board[self.currSqr[0]][self.currSqr[1]][0]
        self.whiteKing = wKing
        self.blackKing = bKing
        self.rooks = rooks
        self.enPassant = enPassant


    def pawnMoves(self):
        possibleMoves = []

        # determine whether this is player white or black's pawn
        if self.color == 'w':
            plr = 1
        else:
            plr = -1

        if -1 < self.currSqr[0]-plr < 8 and -1 < self.currSqr[1] < 8:
            fSqr = self.board[self.currSqr[0]-plr][self.currSqr[1]]
            if not fSqr:
                # the square in front of us is empty :D
                # note because we set plr, 
                # this works if the pawn is black or white :D
                possibleMoves.append([self.currSqr[0]-plr, self.currSqr[1]])

                if -1 < self.currSqr[0]-plr*2 < 8 and -1 < self.currSqr[1] < 8:
                    ffSqr = self.board[self.currSqr[0]-plr*2][self.currSqr[1]]
                    if not ffSqr:
                        if self.currSqr[0] == 6 and plr == 1:
                            possibleMoves.append([self.currSqr[0]-plr*2, self.currSqr[1]])
                        elif self.currSqr[0] == 1 and plr == -1:
                            possibleMoves.append([self.currSqr[0]-plr*2, self.currSqr[1]])
                    

        # now check if this pawn can gobble up any pieces 
        if self.currSqr[1] != 0 and -1 < self.currSqr[0]-plr < 8 and -1 < self.currSqr[1]-1 < 8:
            d1Srq = self.board[self.currSqr[0]-plr][self.currSqr[1]-1]
            d1SrqPos = [self.currSqr[0]-plr, self.currSqr[1]-1]


            if d1Srq and d1Srq[0] != self.color:
                possibleMoves.append([self.currSqr[0]-plr, self.currSqr[1]-1])

            if d1SrqPos in self.enPassant:
                if self.board[d1SrqPos[0]+plr][d1SrqPos[1]]:
                    if self.color != self.board[d1SrqPos[0]+plr][d1SrqPos[1]][0]:
                        if self.board[self.currSqr[0]][self.currSqr[1]-1][0] != self.color: 
                            pos = self.enPassant.index(d1SrqPos)
                            # EN PASSANT MOVE AVAILABLE #
                            possibleMoves.append([self.enPassant[pos][0],
                                self.enPassant[pos][1]])

        
        if self.currSqr[1] != 7 and -1 < self.currSqr[0]-plr < 8 and -1 < self.currSqr[1]+1 < 8:
            d2Srq = self.board[self.currSqr[0]-plr][self.currSqr[1]+1]
            d2SrqPos = [self.currSqr[0]-plr, self.currSqr[1]+1]

            if d2Srq and d2Srq[0] != self.color:
                possibleMoves.append([self.currSqr[0]-plr, self.currSqr[1]+1])

            if d2SrqPos in self.enPassant:
                if self.board[d2SrqPos[0]+plr][d2SrqPos[1]]:
                    if self.color != self.board[d2SrqPos[0]+plr][d2SrqPos[1]][0]:
                        if self.board[self.currSqr[0]][self.currSqr[1]+1][0] != self.color: 
                            pos = self.enPassant.index(d2SrqPos)
                            # EN PASSANT MOVE AVAILABLE #
                            possibleMoves.append([self.enPassant[pos][0],
                                self.enPassant[pos][1]])

        return possibleMoves


    def rookMoves(self):
        possibleMoves = []

        # go up
        k = self.currSqr[0] - 1
        blocked = False
        allowThisMove = True

        while k > -1 and not blocked:
            if self.board[k][self.currSqr[1]]:
                blocked = True
                if self.board[k][self.currSqr[1]][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([k, self.currSqr[1]])

            k -= 1


        # go down
        k = self.currSqr[0] + 1
        blocked = False
        allowThisMove = True

        while k < 8 and not blocked:
            if self.board[k][self.currSqr[1]]:
                blocked = True
                if self.board[k][self.currSqr[1]][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([k, self.currSqr[1]])

            k += 1


        # go left
        k = self.currSqr[1] - 1
        blocked = False
        allowThisMove = True

        while k > -1 and not blocked:
            if self.board[self.currSqr[0]][k]:
                blocked = True
                if self.board[self.currSqr[0]][k][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([self.currSqr[0], k])

            k -= 1


        # go right
        k = self.currSqr[1] + 1
        blocked = False
        allowThisMove = True

        while k < 8 and not blocked:
            if self.board[self.currSqr[0]][k]:
                blocked = True
                if self.board[self.currSqr[0]][k][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([self.currSqr[0], k])

            k += 1


        return possibleMoves


    def bishopMoves(self):
        possibleMoves = []

        # up and right
        k = 1
        blocked = False
        allowThisMove = True
        while self.currSqr[0]-k > -1 and self.currSqr[1]+k < 8  and not blocked:
            if self.board[self.currSqr[0]-k][self.currSqr[1]+k]:
                blocked = True
                if self.board[self.currSqr[0]-k][self.currSqr[1]+k][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([self.currSqr[0]-k, self.currSqr[1]+k])
            k += 1


        # down and right
        k = 1
        blocked = False
        allowThisMove = True
        while self.currSqr[0]+k < 8 and self.currSqr[1]+k < 8  and not blocked:
            if self.board[self.currSqr[0]+k][self.currSqr[1]+k]:
                blocked = True
                if self.board[self.currSqr[0]+k][self.currSqr[1]+k][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([self.currSqr[0]+k, self.currSqr[1]+k])
            k += 1


        # up and left
        k = 1
        blocked = False
        allowThisMove = True
        while self.currSqr[0]-k > -1 and self.currSqr[1]-k > -1  and not blocked:
            if self.board[self.currSqr[0]-k][self.currSqr[1]-k]:
                blocked = True
                if self.board[self.currSqr[0]-k][self.currSqr[1]-k][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([self.currSqr[0]-k, self.currSqr[1]-k])
            k += 1


        # down and left 
        k = 1
        blocked = False
        allowThisMove = True
        while self.currSqr[0]+k < 8 and self.currSqr[1]-k > -1  and not blocked:
            if self.board[self.currSqr[0]+k][self.currSqr[1]-k]:
                blocked = True
                if self.board[self.currSqr[0]+k][self.currSqr[1]-k][0] == self.color:
                    allowThisMove = False
            if allowThisMove:
                possibleMoves.append([self.currSqr[0]+k, self.currSqr[1]-k])
            k += 1

        return possibleMoves


    def horseyMoves(self):
        possibleMoves = []

        for j in range(1, 3):
            for i in range(2):
                r = self.currSqr[0]+(-i)**j+(-1)**j

                c1 = self.currSqr[1]-2+i
                c2 = self.currSqr[1]+2-i

                if -1 < r < 8:
                    if -1 < c1 < 8:
                        piece = self.board[r][c1]
                        if not piece or (piece and piece[0] != self.color):
                            possibleMoves.append([r, c1])

                    if -1 < c2 < 8:
                        piece = self.board[r][c2]
                        if not piece or (piece and piece[0] != self.color):
                            possibleMoves.append([r, c2])


        return possibleMoves


    def kingMoves(self):
        possibleMoves = []


        for j in range(2):
            for i in range(3):
                r = self.currSqr[0]+(-1)**j
                c = self.currSqr[1]-1+i


                if -1 < r < 8 and -1 < c < 8:
                    s1 = self.board[r][c]

                    if not s1 or (s1 and s1[0] != self.color):
                        possibleMoves.append([r,c])


        for i in range(2):
            r = self.currSqr[0]
            c = self.currSqr[1]+(-1)**i

            if -1 < r < 8 and -1 < c < 8:
                s1 = self.board[r][c]

                if not s1 or (s1 and s1[0] != self.color):
                    possibleMoves.append([r,c])

        # check for castling
        if self.color == 'w':
            king = self.whiteKing
            col = 7
        else: 
            king = self.blackKing
            col = 0
        
        # check if this king hasn't moved
        if len(king) == 1 and king[0] == [col, 4]:
            # check if there is space to castle
            available = True

            # King side
            for i in range(2):
                if self.board[col][5+i]:
                    available = False

            if self.rooks.count(self.color+'Rk') == 0 and available:
                if self.color+'Rk' == self.board[col][7]:
                    possibleMoves.append([col,6])


            # Queen side
            available = True
            for i in range(3):
                if self.board[col][3-i]:
                    available = False

            if self.rooks.count(self.color+'Rq') == 0 and available:
                if self.color+'Rq' == self.board[col][0]:
                    possibleMoves.append([col,2])

        return possibleMoves


    def queenMoves(self):
        possibleMoves = []

        possibleMoves.extend(self.rookMoves())
        possibleMoves.extend(self.bishopMoves())
        
        return possibleMoves


    def getPieceMoves(self):
        possibleMoves = []
        if self.piece == 'P':
            possibleMoves = self.pawnMoves()

        elif self.piece == 'R':
            possibleMoves = self.rookMoves()

        elif self.piece == 'N':
            possibleMoves = self.horseyMoves()

        elif self.piece == 'B':
            possibleMoves = self.bishopMoves()

        elif self.piece == 'Q':
            possibleMoves = self.queenMoves()

        elif self.piece == 'K':
            possibleMoves = self.kingMoves()

        return possibleMoves



if __name__ == "__main__":
    g = GameLogic()




