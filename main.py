# Faisal Mashhadi
# fmashhad
# This file handles the user input, client code of the multiplayer feature,
# and getting moves from the ChessAI file to display it to your screen
# In essence this file handles the UI with the user

from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase

from panda3d.core import CollisionTraverser, CollisionHandlerQueue
from panda3d.core import CollisionNode, CollideMask, BitMask32, CollisionRay
from panda3d.core import AmbientLight, Vec4, DirectionalLight, PointLight

from panda3d.core import NodePath
from direct.task import Task
from direct.gui import DirectGui
from direct.gui.OnscreenText import OnscreenText

import os, sys, sockets, tkinter
from tkinter import messagebox

from ChessEngine import GameLogic
from ChatClient import chatComm
from ChessAI import basicAI

# sets up the title for the panda window to "The Queen's Gambit'"
loadPrcFileData('', 
                '''window-title The Queen's Gambit''')

PATH = os.getcwd() + '/'

class Chess(ShowBase):

    def __init__(self, mode, p1, p2, color='', chatConn=''):
        # setup ShowBase instance
        ShowBase.__init__(self)

        
        # setup background music and sound effects
        self.mySound = self.loader.loadSfx("Sounds/Chillout-downtempo-music-loop.mp3")
        self.mySound.setLoop(True)
        self.mySound.play()
        self.mySound.setVolume(0.2)
        
        self.beep = self.loader.loadSfx("Sounds/click.mp3")
        self.beep.setVolume(0.6)

        self.beep2 = self.loader.loadSfx("Sounds/click2.mp3")
        self.beep2.setVolume(0.6)

        self.buttonError = self.loader.loadSfx("Sounds/error.mp3")
        self.buttonError.setVolume(0.6)

        # setup engine reference and get board
        self.Engine = GameLogic()
        self.boardState = self.Engine.getBoard()
        self.player = self.Engine.getPlayer()

        # setup name of the players
        self.nameP1 = p1
        self.nameP2 = p2

        # This variable determines whether the end of the game has been
        # reached or not 
        self.end = False

        # Determines which player you're playing as
        if color:
            self.myColor = color
            # set camera view based on myColor
            if self.myColor == 'w':
                self.view = 2
                self.changeView()
                self.enemyColor = 'b'
            elif self.myColor == 'b':
                self.view = 0
                self.changeView()
                self.enemyColor = 'w'

        # If this is true, then you're playing online
        if chatConn:
            self.chatConn = chatConn
            
            self.resignButton = DirectGui.DirectButton(text=('Resign'),
                                        pos=(1.1,1.1,-0.9), scale=0.05, 
                                        command=lambda x='R': self.sendP2(x))
            self.drawButton = DirectGui.DirectButton(text=('Offer Draw'),
                                        pos=(1.1,1.1,-0.8), scale=0.05, 
                                        command=lambda x='D': self.sendP2(x))

            self.undoButton = DirectGui.DirectButton(text=('Request Undo'),
                                        pos=(1.1,1.1,-0.7), scale=0.05, 
                                        command=lambda x='U': self.sendP2(x))
            

            self.allowDrawRequestThisMove = True
            self.allowUndoRequestThisMove = True
            self.timerP1 = 600
            self.timerP2 = 600
            self.passedTime = 0

            # Show timer on screen if online
            self.timerP1Label = OnscreenText(text ='10:00', 
                            pos = (-.5,-.95), scale = .05, mayChange=True)

            self.timerP2Label = OnscreenText(text ='10:00', 
                            pos = (.5,-.95), scale = .05, mayChange=True)

            if self.myColor == 'b':
                self.taskMgr.doMethodLater(1.0, self.waitForOpponent, "WaitingForOpponent")
            else:
                self.taskMgr.doMethodLater(1.0, self.startTemporaryTimer, "WaitingForFirstMove")


        # Save the mode you're playing in in this variable
        self.mode = mode

        # setup AI configurations (if the mode is AI)
        if self.mode == 'AI':
            if self.myColor == 'w':
                self.AIToPlay = False
            else:
                self.AIToPlay = True

            self.AI = basicAI(self.enemyColor)
            self.accept('z', self.undo)
            self.taskMgr.doMethodLater(.5, self.makeAIMove, "AIHandler")

        
        # disable camera movement
        self.disableMouse()
        self.end = False


        # setup button to change camera view
        self.viewButton = DirectGui.DirectButton(text=('Change View'),
                                        pos=(1.1,1.1,0.9), scale=0.05, command=self.changeView)

        # setup button to change theme
        self.themeButton = DirectGui.DirectButton(text=('Change Theme'),
                                        pos=(1.1,1.1,0.8), scale=0.05, command=self.changeTheme)


        # setup lighting
        '''
        IMPORTED CODE BELOW
        '''

        # setup ambient light
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(self.ambientLightNodePath)

        # setup direct light
        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(90, -90, 0)
        render.setLight(self.mainLightNodePath)

        '''
        END OF IMPORTED CODE
        SOURCE:
        https://arsthaumaturgis.github.io/Panda3DTutorial.io/tutorial/tut_lesson03.html
        '''
        

        # sets up collision traverser and handler 
        # Also sets up ray from the camera
        ''' 
        IMPORTED CODE BELOW
        '''

        # setup the CollisionTraverser  and a CollisionHandler
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue() 

        # setup a ray from the cam 
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = self.cam.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))

        # attach CollisionRay Node to cam (pickerNode)
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP,self.pq)

        '''
        END OF IMPORTED CODE
        SOURCE: 
        https://discourse.panda3d.org/t/not-able-to-click-3d-objects-and-move-them/12546/10
        '''


        # setup board root (reference point for tiles)
        self.boardRoot = loader.loadModel(f"{PATH}Models/board.obj")
        self.boardRoot.setHpr(0,90,0)
        self.boardRoot.reparentTo(render)


        # setup tile selection
        self.selectedTiles = []

        
        # sets up tiles
        self.tileHolders = []
        self.alltTextures = [loader.loadTexture(f"{PATH}/Textures/lightbrown.png"),
                    loader.loadTexture(f"{PATH}/Textures/wood.png"),
                    loader.loadTexture(f"{PATH}/Textures/white.jpg"),
                    loader.loadTexture(f"{PATH}/Textures/blacklines.jpg"),
                    loader.loadTexture(f"{PATH}/Textures/pink.jpg"),
                    loader.loadTexture(f"{PATH}/Textures/purple.jpg"),
                    loader.loadTexture(f"{PATH}/Textures/beige.jpg"),
                    loader.loadTexture(f"{PATH}/Textures/green.jpg")]

        self.texture = 0
        self.tTextures = [self.alltTextures[0],self.alltTextures[1]]
        
        # sets up pieces
        self.pieceHolders = {}
        pPATH = PATH + 'Models/'
        self.pTextures = [loader.loadTexture(f"{PATH}/Textures/whitefabric.jpg"),
                              loader.loadTexture(f"{PATH}/Textures/black.jpg")]
        self.pieces = {'K': loader.loadModel(f"{pPATH}K.obj"),
                 'Q': loader.loadModel(f"{pPATH}Q.obj"),
                 'R': loader.loadModel(f"{pPATH}R.obj"),
                 'B': loader.loadModel(f"{pPATH}B.obj"),
                 'N': loader.loadModel(f"{pPATH}N.obj"),
                 'P': loader.loadModel(f"{pPATH}P.obj")}

        
        # setup other random stuff
        self.drawBoard()
        self.choosingTitle = False
        self.titleButtons = []
        self.coolDown = 0
        self.timer = []
        self.allowChanging = False

        # setup event handlers for user input
        self.accept('x', self.changingCamera)
        self.accept('mouse1',self.mouseTask)
        self.accept('escape', lambda: self.endHandler("NO"))

        # show wins and player stats
        self.plr1Color, self.plr2Color = '', ''
        self.plr1WinsText, self.plr2WinsText, self.drawsText = '', '', ''
        self.displayWins()

    
    def drawPieces(self, pieceHolders, pieces, boardState, texture):
        # loop through all the squares in a chess board
        for r in range(8):
            for c in range(8):
                piece = boardState[r][c]
                if piece: # checks if the current square has a piece
                    # make an instance of this piece in current sqaure
                    model = pieces[piece[1]]
                    placeholder = render.attachNewNode("Piece-Placeholder") 
                    placeholder.setHpr(0,90,0)
                    placeholder.setPos(7-(2*c), -7+(2*r), 0.05)

                    # check if the piece is black or whie to apply texture
                    if 'w' in piece:
                        placeholder.setTexture(texture[0])
                    else:
                        placeholder.setTexture(texture[1])
                        placeholder.setHpr(180,90,0)

                    # reparent the model to the placeholder
                    model.instanceTo(placeholder)
                    pieceHolders[f"{r}{c}"] = placeholder


    def drawTiles(self, tileHolders, board, textures):
        for r in range(8):
            for c in range(8):
                tile = loader.loadModel(f"{PATH}/Models/Tile.obj")
                tile.setPos(7-(2*c), 0, 7-(2*r))
                tile.setTexture(textures[(r+c)%2])
                tile.reparentTo(board)
                tile.setTag('Tile', f"{r}{c}")
                tile.setCollideMask(BitMask32.bit(1))

                tileHolders.append(tile)


    def drawBoard(self):
        self.removePiecesAndTiles(self.pieceHolders, self.tileHolders)
        self.drawTiles(self.tileHolders, self.boardRoot, self.tTextures)
        self.drawPieces(self.pieceHolders, self.pieces, self.boardState,
                        self.pTextures)
        

    def removePiecesAndTiles(self, pieceHolders, tileHolders):
        for i in pieceHolders:
            pieceHolders.get(i).removeNode()

        pieceHolders.clear()

        for j in tileHolders:
            j.removeNode()

        tileHolders.clear()


    def undo(self):
        if self.coolDown < 2:
            if self.Engine.undoMove() and not self.end:
                if self.mode == 'AI':
                    if not self.AIToPlay:
                        if self.Engine.undoMove() and not self.end:
                            self.Engine.switchPlayer()
                            self.player = self.Engine.getPlayer()
                            self.drawBoard()
                            
                self.coolDown += 1
                self.Engine.switchPlayer()
                self.player = self.Engine.getPlayer()
                self.selectedTiles.clear()
                self.drawBoard()

                if self.allowChanging:
                    if self.player == 'w':
                        self.view = 2
                        self.changeView()
                    else:
                        self.view = 3
                        self.changeView()


        else:

            if len(self.timer) == 0:
                # Make sure no other text is being displayed on screen
                temp = OnscreenText(
                    text = 'You cannot undo twice in a row.', 
                    pos = (0, 0.9), scale = .1)

                self.timer.append(10)
                whichTimer = len(self.timer)-1

                self.taskMgr.add(self.displayWarning, f"UNDO{whichTimer}", 
                                        extraArgs=[f"UNDO{whichTimer}", temp, whichTimer])


    def displayWarning(self, task, text, whichTimer):
        self.timer[whichTimer] -= .1
        
        if self.timer[whichTimer] < 0: 
            # The timer ran ou, so destroy this text
            self.timer[whichTimer] = 0
            text.destroy()
            self.taskMgr.remove(task)
            
            if self.timer.count(0) == len(self.timer):
                self.timer = []

        return Task.cont


    def mouseTask(self):
        '''
                IMPORTED CODE BELOW
        '''
        # check if mouse is in screen and is not clicking on a GUI object
        if base.mouseWatcherNode.hasMouse():

            # gets the mouse position
            mpos = base.mouseWatcherNode.getMouse()

            # set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode,mpos.getX(),mpos.getY())
            self.picker.traverse(render)
            
            # if we have hit something sort the hits so that the closest is first and highlight the node
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()

                ''' 
                END OF IMPORTED CODE
                SOURCE: 
                https://discourse.panda3d.org/t/not-able-to-click-3d-objects-and-move-them/12546/10
                '''

                # make sure user clicked on a tile
                # and make sure the user isn't promoting a pawn or the game isn't over
                if pickedObj and not self.choosingTitle and not self.end:
                    self.beep.play()
                    objectTag = pickedObj.findNetTag('Tile')
                    pickedObj = pickedObj.getNetTag('Tile')
                    self.selectedTiles.append([pickedObj, objectTag])


                    row = int(self.selectedTiles[0][0][0])
                    col = int(self.selectedTiles[0][0][1])
                    board = self.boardState
                    chessPiece = board[row][col]

                    if len(self.selectedTiles) == 1:
                        if chessPiece and chessPiece[0] == self.player and chessPiece[0] == self.myColor:
                            # highlight potential squares if the player is correct
                            self.highlightTiles([row, col], "NORMAL")
                        else:
                            # an empty sqaure was selected, clear selectedTiles
                            # or opponent's piece was selected, so clear selectedTIles
                            self.selectedTiles.clear()

                            
                    elif len(self.selectedTiles) == 2:
                        # make sure user didnt move the piece to the same sqaure
                        if self.selectedTiles[0] != self.selectedTiles[1]:
                            currRow = int(self.selectedTiles[0][0][0])
                            currCol = int(self.selectedTiles[0][0][1])

                            toRow = int(self.selectedTiles[1][0][0])
                            toCol = int(self.selectedTiles[1][0][1])

                            # user selected another one of their pieces
                            if self.boardState[toRow][toCol] and self.boardState[toRow][toCol][0] == self.player:
                                # so deselct previous selections
                                self.selectedTiles.clear()
                                    
                                # add this current selection if it is the same as the player's
                                self.drawBoard()
                                self.selectedTiles.append([pickedObj, objectTag])
                                self.highlightTiles([toRow, toCol], "NORMAL")


                            # see if this is a valid move and make it if it is
                            else:
                                move = 'WAITING FOR MOVE'
                                color = chessPiece[0]

                                if self.player == color and color == self.myColor:
                                    # make sure its the correct player's turn
                                    self.drawBoard()
                                    move = self.Engine.makeMove([currRow, currCol], [toRow, toCol])
                                else:
                                    move = 'INCORRECT PLAYER'

                                if move == "SUCCESS":
                                    self.coolDown = 0
                                    self.highlightTiles([toRow, toCol], "ORANGE")
                                    newPiece, label = self.setupAnimation([currRow, currCol], [toRow, toCol])
                                    self.boardState = self.Engine.getBoard()
                                    if self.mode == "Multiplayer":
                                        self.passedTime = 0
                                        self.chatConn.sendMessage(self.nameP2, f"{currRow}{currCol}{toRow}{toCol}")
                                        self.chatConn.sendMessage(self.nameP2, f"TIMER: {self.timerP1}")
                                    
                                    # set speed for animation
                                    s1, s2 = .2, .2
                                    
                                    # Knight pieces have different speed animations because
                                    # they move weirdly
                                    if label == 'N':
                                        if abs(currRow - toRow) == 2:
                                            s1, s2 = .1, .2
                                        else:
                                            s1, s2 = .2, .1

                                    # Make sure each animation has its own ID to avoid duplicate pieces appearing
                                    ID = f"{currRow}{currCol}-{toRow}{toCol}"
                                    
                                    # animate by adding the playAnimation function to the task Manager
                                    self.taskMgr.add(self.playAnimation, f"Animation{ID}", 
                                        extraArgs=[newPiece, [7-(toCol*2), -7+(toRow*2)], s1, s2, ID])
                                    
                                    
                            
                                    # switch player and check if the game is over
                                    self.Engine.switchPlayer()

                                    if self.mode != 'AI':
                                        self.evaluateGame() 

                                elif move == 'PROMOTION':
                                    self.highlightTiles([toRow, toCol], "ORANGE")
                                    s1, s2 = .2, .2
                                    
                                    ID = f"{currRow}{currCol}-{toRow}{toCol}"
                                    newPiece, label = self.setupAnimation([currRow, currCol], [toRow, toCol])
                                    
                                    self.taskMgr.add(self.playAnimation, f"Animation{ID}", 
                                        extraArgs=[newPiece, [7-(toCol*2), -7+(toRow*2)], s1, s2, ID])
                                    
                                    title = self.askForPromotionTitle([toRow, toCol, currRow, currCol])



                                    if self.mode != 'AI':
                                        self.evaluateGame()


                                self.player = self.Engine.getPlayer()
                                self.selectedTiles.clear()

                                if move == 'REJECTED':
                                    self.drawBoard()
                                    self.highlightTiles([currRow, currCol], "RED")
                                    
                        else:
                            # the same sqaure was selected, so deselect it
                            self.selectedTiles.clear()
                            self.drawBoard()
            else:
                # user clicked outside board, so clear selections
                self.selectedTiles.clear()
                self.drawBoard()


    def waitForOpponent(self, task):
        newMessages, newFiles = self.chatConn.getMail()
        update = False

        if newMessages != [] and not self.end:
            for u,m in newMessages:
                if u == self.nameP2:
                    if m == "Draw?":
                        popUp = tkinter.messagebox.askquestion('Draw?',
                                    f'{u} is offering you a draw. Do you accept?')

                        if popUp == 'yes':
                            self.chatConn.sendMessage(u, "Draw Accepted.")
                            mate = OnscreenText(text='Draw.', pos = (0,0.2), scale = .3)
                            textObject = OnscreenText(text = 'NO ONE WON.', 
                                pos = (0,0), scale = .1)
                            wins[2] += 1
                            self.taskMgr.add(self.gameOverCam, "END")
                            self.end = True

                        else:
                            self.chatConn.sendMessage(u, "Draw Declined!")

                    elif m == "I Resign" or m == "I Quit.":
                        if self.myColor == 'w':

                            mate = OnscreenText(text = 'Opponent Resigned.', pos = (0,0.2), scale = .2)
                            textObject = OnscreenText(text = 'WHITE WON THE GAME!', 
                                pos = (0,0), scale = .1)

                            if (wins[0] + wins[1] + wins[2])%2 == 0:
                                wins[0] += 1
                            else:
                                wins[1] += 1

                        else:
                            mate = OnscreenText(text = 'Opponent Resigned.', pos = (0,0.2), scale = .2)
                            textObject = OnscreenText(text = 'BLACK WON THE GAME!', 
                                pos = (0,0), scale = .1)


                            if (wins[0] + wins[1] + wins[2])%2 == 0:
                                wins[1] += 1
                            else:
                                wins[0] += 1


                        self.taskMgr.add(self.gameOverCam, "END")
                        self.end = True


                    elif m == "Undo?":
                        popUp = tkinter.messagebox.askquestion('Undo?',
                                    f'{u} is requesting an undo. Do you accept?')

                        if popUp == 'yes':
                            self.chatConn.sendMessage(u, "Undo Accepted.")
                            self.undo()
                            self.undo()

                        else:
                            self.chatConn.sendMessage(u, "Undo Declined!")

                    elif "Declined" in m:
                        if m == "Undo Declined!":
                            tkinter.messagebox.showinfo('Declined',
                                f'{u} has declined to undo.')
                        if m == "Draw Declined!":
                            tkinter.messagebox.showinfo('Declined',
                                f'{u} has declined to draw.')

                    
                    elif "Accepted" in m:
                        if m == "Undo Accepted.":
                            self.undo()
                            self.undo()

                            temp = OnscreenText(
                            text = "Undo Accepted.", 
                            pos = (0, 0.9), scale = .08)

                            self.timer.append(10)
                            whichTimer = len(self.timer)-1

                            self.taskMgr.add(self.displayWarning, f"UNDOACCEPT{whichTimer}", 
                                            extraArgs=[f"UNDOACCEPT{whichTimer}", temp, whichTimer])

                        if m == "Draw Accepted.":
                            mate = OnscreenText(text='Draw.', pos = (0,0.2), scale = .3)
                            textObject = OnscreenText(text = 'NO ONE WON.', 
                                pos = (0,0), scale = .1)
                            wins[2] += 1

                            self.taskMgr.add(self.gameOverCam, "END")
                            self.end = True


                    elif m[:6] == "TIMER:":
                        self.timerP2 = int(m[7:])


                    elif m[:9] == "PROMOTION":
                        if self.boardState[int(m[10])][int(m[11])]:
                            if self.boardState[int(m[10])][int(m[11])][1] == "P":
                                self.passedTime = 0
                            
                                self.allowDrawRequestThisMove = True
                                self.allowUndoRequestThisMove = True
                                self.taskMgr.remove("WaitingForOpponent")
                                self.Engine.setBoard([int(m[12]), int(m[13])],
                                            self.Engine.getPlayer()+m[9])
                                self.Engine.setBoard([int(m[10]), int(m[11])], '')
                                self.Engine.switchPlayer()

                                self.drawBoard()
                                        
                                self.evaluateGame() 
                                self.player = self.Engine.getPlayer()
                                self.selectedTiles.clear()


                    
                    elif len(m) == 4:
                        isDigit = True
                        for i in m:
                            if i not in "0123456789":
                                isDigit = False

                        if isDigit == True:
                            m = int(m)
                            m1,m2, m3, m4 = m//1000, (m//100)%10, (m//10)%10, m%10

                            move = self.Engine.makeMove(
                                [m1, m2], [m3, m4])


                        else:
                            move = "NOPE"
                    
                        if move == "SUCCESS":
                            self.passedTime = 0
                            
                            self.allowDrawRequestThisMove = True
                            self.allowUndoRequestThisMove = True
                            self.taskMgr.remove("WaitingForOpponent")
                            
                            self.highlightTiles([m3, m4], "ORANGE")
                            newPiece, label = self.setupAnimation([m1, m2], 
                                [m3, m4])
                            s1, s2 = .2, .2

                            if label == "N":
                                if abs(m1 - m3) == 2:
                                    s1, s2 = .1, .2
                                else:
                                    s1, s2 = .2, .1

                            ID = f"{m1}{m2}-{m3}{m4}"

                            self.taskMgr.add(self.playAnimation, f"Animation{ID}", 
                                extraArgs=[newPiece, [7-(m4*2), -7+(m3*2)], 
                                s1, s2, ID])

                            self.Engine.switchPlayer()

                            self.evaluateGame() 

                            self.player = self.Engine.getPlayer()
                            self.selectedTiles.clear()
                            
                            if len(self.Engine.moveLog) == 1 and self.myColor == 'b':
                                taskMgr.doMethodLater(1.0, self.timerHandler,
                                                      'keepTimer')


        return Task.cont


    def sendP2(self, command):
        if self.myColor == self.player:
            self.beep2.play()
            
            if command == 'D':
                if self.allowDrawRequestThisMove:
                    self.allowDrawRequestThisMove = False
                    self.chatConn.sendMessage(self.nameP2, "Draw?")
                    tkinter.messagebox.showinfo('Success!',
                                                'Draw request sent successfully.')
                    self.taskMgr.doMethodLater(1.0, self.waitForOpponent, "WaitingForOpponent")
                else:
                    tkinter.messagebox.showinfo('Not Allowed!',
                    'You cannot request for a draw twice on the same move')

            elif command == 'U':
                if len(self.Engine.moveLog) > 1:
                    if self.allowUndoRequestThisMove:
                        self.allowUndoRequestThisMove = False
                        self.chatConn.sendMessage(self.nameP2, "Undo?")
                        self.taskMgr.doMethodLater(1.0, self.waitForOpponent, "WaitingForOpponent")
                    else:
                        tkinter.messagebox.showinfo('Not Allowed!',
                    'You cannot request for an undo twice on the same move')
                        
                else:
                    temp = OnscreenText(
                    text = "There are no moves to undo.", 
                    pos = (0, 0.9), scale = .08)

                    self.timer.append(10)
                    whichTimer = len(self.timer)-1

                    self.taskMgr.add(self.displayWarning, f"UNDOERROR{whichTimer}", 
                                    extraArgs=[f"UNDOERROR{whichTimer}", temp, whichTimer])


            elif command == 'R':
                popUp = tkinter.messagebox.askquestion('Resign?',
                    'Are you sure you want to resign this game?')

                if popUp == 'yes':
                    self.chatConn.sendMessage(self.nameP2, "I Resign")
                    if self.myColor == 'w':

                        mate = OnscreenText(text = 'You Resigned.', pos = (0,0.2), scale = .3)
                        textObject = OnscreenText(text = 'BLACK WON THE GAME!', 
                            pos = (0,0), scale = .1)

                        if (wins[0] + wins[1] + wins[2])%2 == 0:
                            wins[1] += 1
                        else:
                             wins[0] += 1
                    else:
                        mate = OnscreenText(text = 'You Resigned.', pos = (0,0.2), scale = .3)
                        textObject = OnscreenText(text ='WHITE WON THE GAME!', 
                            pos = (0,0), scale = .1)

                        if (wins[0] + wins[1] + wins[2])%2 == 0:
                            wins[0] += 1
                        else:
                            wins[1] += 1

                    self.taskMgr.add(self.gameOverCam, "END")
                    self.end = True
        else:
            self.buttonError.play()
            temp = OnscreenText(
            text = "You cannot send a request during your opponent's turn", 
            pos = (0, 0.9), scale = .06)

            self.timer.append(8)
            whichTimer = len(self.timer)-1

            self.taskMgr.add(self.displayWarning, f"OPPONENT{whichTimer}", 
                            extraArgs=[f"OPPONENT{whichTimer}", temp, whichTimer])



    def evaluateGame(self):
        gameOver = self.Engine.isGameOver()
                                    
        if gameOver != 'Continue':
            self.taskMgr.add(self.gameOverCam, "END")
            self.end = True
            if gameOver == "StaleMate":
                ### STALEMATE ###
                textObject = OnscreenText(text ='STALEMATE!', pos = (0,0), scale = .1)
                wins[2] += 1
                
            elif gameOver == "CheckMate":
                plr = self.Engine.getPlayer()

                if plr == 'w':
                    ### BLACK WON THE GAME ###
                    mate = OnscreenText(text ='CHECKMATE!', pos = (0,0.2), scale = .3)
                    textObject = OnscreenText(text ='BLACK WON THE GAME!', 
                        pos = (0,0), scale = .1)


                    if (wins[0] + wins[1] + wins[2])%2 == 0:
                        wins[1] += 1
                    else:
                        wins[0] += 1
                                            
                else:
                    ### WHITE WON THE GAME ###
                    mate = OnscreenText(text ='CHECKMATE!', pos = (0,0.2), scale = .3)
                    textObject = OnscreenText(text ='WHITE WON THE GAME!', 
                        pos = (0,0), scale = .1)

                    if (wins[0] + wins[1] + wins[2])%2 == 0:
                        wins[0] += 1
                    else:
                        wins[1] += 1
                                        
            elif gameOver == "Not Enough Material":
                ### DRAW! NOT ENOUGH MATERIAL ###
                textObject = OnscreenText(text ='DRAW! INSUFFICIENT MATERIAL LEFT', 
                    pos = (0,0), scale = .1)


    def playAI(self, task):
        if self.end != True:
            myMoveLog = self.Engine.getMoveLog()[:]
            move = self.AI.getSmartMove(myMoveLog, self.Engine.getBoard())[1]
            currRow, currCol = move[0][0], move[0][1]
            toRow, toCol = move[1][0], move[1][1]
            

            if self.boardState[currRow][currCol] and self.boardState[currRow][currCol][1] == 'P':
                # Pawn promotion
                
                if toRow == 7 or toRow == 0:
                    self.Engine.setBoard([currRow, currCol], '')
                    self.Engine.setBoard([toRow, toCol],
                                            self.Engine.getPlayer()+'Q')
                    self.Engine.moveLog.append(["MANUAL", [currRow, currCol, toRow, toCol],
                                                self.Engine.getPlayer()+'Q'])
                    self.boardState = self.Engine.getBoard()
                else:
                    move = self.Engine.makeMove(
                    [currRow, currCol], [toRow, toCol])
                self.boardState = self.Engine.getBoard()

            else:
                move = self.Engine.makeMove(
                    [currRow, currCol], [toRow, toCol])
                self.boardState = self.Engine.getBoard()
            
            self.beep.play()
            self.highlightTiles([toRow, toCol], "ORANGE")
            newPiece, label = self.setupAnimation([currRow, currCol], [toRow, toCol])
                                                
            s1, s2 = .2, .2
                                                
            if label == 'N':
                if abs(currRow - toRow) == 2:
                    s1, s2 = .1, .2
                else:
                    s1, s2 = .2, .1
                    
            self.Engine.switchPlayer()
            ID = f"{currRow}{currCol}-{toRow}{toCol}"
            self.taskMgr.add(self.playAnimation, f"Animation{ID}", 
                extraArgs=[newPiece, [7-(toCol*2), -7+(toRow*2)], s1, s2, ID])
                                            
            self.selectedTiles.clear()
            self.AIToPlay = False
            self.taskMgr.remove(task)
            
        self.taskMgr.remove(task)
                

    def askForPromotionTitle(self, pos):
        title = ''
        self.choosingTitle = True

        button1 = DirectGui.DirectButton(text=('Queen'),
                                        pos=(0,1.1,0.9), scale=0.05, 
                                        command=self.setTitle, extraArgs=[pos, 'Q'])

        button2 = DirectGui.DirectButton(text=('Rook'),
                                        pos=(0,1.1,0.8), scale=0.05, 
                                        command=self.setTitle, extraArgs=[pos, 'R'])

        button3 = DirectGui.DirectButton(text=('Bishop'),
                                        pos=(0,1.1,0.7), scale=0.05, 
                                        command=self.setTitle, extraArgs=[pos, 'B'])

        button4 = DirectGui.DirectButton(text=('Knight'),
                                        pos=(0,1.1,0.6), scale=0.05, 
                                        command=self.setTitle, extraArgs=[pos, 'N'])

        self.titleButtons = [button1, button2, button3, button4]


    def setTitle(self, pos, title):
        self.beep2.play()
        
        self.choosingTitle = False
        self.Engine.setBoard([pos[0], pos[1]], self.Engine.getPlayer()+title)
        self.Engine.moveLog.append(["PROMOTION", [pos[2], pos[3], pos[0], pos[1]]])

        if self.mode == 'AI':
            if self.Engine.getPlayer() == self.enemyColor:
                self.AIToPlay = True
                self.taskMgr.doMethodLater(.5, self.makeAIMove, "AIHandler")
            else:
                self.Engine.switchPlayer()
        else:
            self.chatConn.sendMessage(self.nameP2,
                            f'PROMOTION{title}{pos[2]}{pos[3]}{pos[0]}{pos[1]}')
        self.evaluateGame()
        self.drawBoard()

        for button in self.titleButtons:
            button.destroy()


    def highlightTiles(self, pos, color):
        currTile = self.tileHolders[pos[0]*8+pos[1]]

        if color == "ORANGE":
            currTile.setColor(2,1.5,0)

        if color == "RED":
            currTile.setColor(2,0,0)
        
        if color == "NORMAL":
            allTiles = self.Engine.getValidSquares(pos)
            currTile.setColor(0,2,0)

            for tile in range(len(allTiles)):
                currTile = self.tileHolders[allTiles[tile][0]*8+allTiles[tile][1]]
                currTile.setColor(0,2,0)


    def setupAnimation(self, currPos, toPos):
        piece = self.boardState[toPos[0]][toPos[1]]
        newPiece = loader.loadModel(f"{PATH}/Models/{piece[1]}.obj")
        newPiece.setHpr(0,90,0)
        newPiecePos = [7-(2*currPos[1]), -7+(2*currPos[0])]
        newPiece.setPos(newPiecePos[0], newPiecePos[1], 0.05)
        newPiece.reparentTo(render)

        if 'w' in piece:
            newPiece.setTexture(self.pTextures[0])
        else:
            newPiece.setTexture(self.pTextures[1])
            newPiece.setHpr(180,90,0)

        if self.pieceHolders and f"{currPos[0]}{currPos[1]}" in self.pieceHolders:
            pieceNode = self.pieceHolders[f"{currPos[0]}{currPos[1]}"].removeNode()

        return newPiece, piece[1]


    def playAnimation(self, newPiece, toPos, s1, s2, ID):
        pos = newPiece.getPos()
        
        if abs(pos[1] - toPos[1]) > .1:
            if toPos[1] > pos[1]:
                if abs(pos[0] - toPos[0]) > .1:
                    if toPos[0] > pos[0]:
                        newPiece.setPos(pos[0]+s1, pos[1]+s2, 0.05)
                    elif pos[0] > toPos[0]:
                        newPiece.setPos(pos[0]-s1, pos[1]+s2, 0.05)
                else:
                    newPiece.setPos(pos[0], pos[1]+s1, 0.05)
            
            elif pos[1] > toPos[1]:
                if abs(pos[0] - toPos[0]) > .1:
                    if toPos[0] > pos[0]:
                        newPiece.setPos(pos[0]+s1, pos[1]-s2, 0.05)
                    elif pos[0] > toPos[0]:
                        newPiece.setPos(pos[0]-s1, pos[1]-s2, 0.05)
                else:
                    newPiece.setPos(pos[0], pos[1]-s1, 0.05)

        elif abs(pos[0] - toPos[0]) > .1:
            if toPos[0] > pos[0]:
                newPiece.setPos(pos[0]+s1, pos[1], 0.05)
            
            elif pos[0] > toPos[0]:
                newPiece.setPos(pos[0]-s1, pos[1], 0.05)

        else:
            # The animation ended, so delete this animated piece
            self.taskMgr.remove(f"Animation{ID}")
            newPiece.removeNode()
            self.selectedTiles.clear()
            self.drawBoard()
            self.boardState = self.Engine.getBoard()

            if self.allowChanging:
                # Switch the camera posiiont too (if it is not disabled)
                if self.player == 'w':
                    self.view = 2
                    self.changeView()
                else:
                    self.view = 3
                    self.changeView()

            if self.mode == 'Multiplayer':
                if self.myColor != self.player:
                    self.taskMgr.doMethodLater(1.0, self.waitForOpponent, "WaitingForOpponent")

                    if len(self.Engine.moveLog) == 1:
                        taskMgr.doMethodLater(1.0, self.timerHandler, 'keepTimer')

            elif self.mode == 'AI':
                self.evaluateGame()
                self.player = self.Engine.getPlayer()
                # This move has ended, so switch the player's turn
                if self.player != self.myColor:
                    self.AIToPlay = True
                else:
                    if self.allowChanging:
                        if self.player == 'w':
                            self.view = 2
                            self.changeView()
                        else:
                            self.view = 3
                            self.changeView()


        return Task.cont


    def makeAIMove(self, task):
        if self.AIToPlay is True and not self.end:
            self.taskMgr.doMethodLater(1, self.playAI, "AITURN")
            self.AIToPlay = False

        return Task.cont


    def changeView(self):
        if not self.end:
            self.beep2.play()
            self.view += 1
            pos = self.view % 3
            if pos == 0:
                # white player point of view
                self.cam.setPos(0.25,16,35)
                self.cam.setHpr(180,-65,0)
                
            if pos == 1:
                # black player point of view
                self.cam.setPos(-0.25,-16,35)
                self.cam.setHpr(0,-65,0)

            if pos == 2:
                # side point of view
                self.cam.setPos(16,0,35)
                self.cam.setHpr(90,-65,0)


    def changeTheme(self):
        if not self.end:
            self.beep2.play()
            self.texture += 2

            num = len(self.alltTextures)
            text1 = (self.texture)%num
            text2 = (self.texture+1)%num
            
            self.tTextures = [self.alltTextures[text1], self.alltTextures[text2]]

            self.drawBoard()


    def changingCamera(self):
        if not self.choosingTitle and not self.end:
            if len(self.timer) == 0:
                self.allowChanging = not self.allowChanging
                if self.allowChanging:
                    switchCamtext = OnscreenText(
                                text = 'Switching the camera has been enabled.', 
                                pos = (0, 0.8), scale = .08)
                else:
                     switchCamtext = OnscreenText(
                                text = 'Switching the camera has been disabled.', 
                                pos = (0, 0.8), scale = .08)

                self.timer.append(8)
                whichTimer = len(self.timer)-1

                self.taskMgr.add(self.displayWarning, f"CAMERA{whichTimer}", 
                                    extraArgs=[f"CAMERA{whichTimer}", switchCamtext, whichTimer])


    def gameOverCam(self, task):
        hpr = self.cam.getHpr()
        pos = self.cam.getPos()
        
        if hpr[1] < -55:
            self.cam.setHpr(hpr[0], hpr[1]+.1, hpr[2])
            self.cam.setPos(pos[0], pos[1], pos[2]+.1)
        else:
            self.taskMgr.remove("END")
            self.displayWins(True)
            self.viewButton.destroy()
            self.themeButton.destroy()

            if not self.mode == "Multiplayer":
                playAgainText = OnscreenText(
                    text='Play Again?', pos = (0,-0.2), scale = .08)
                yes = DirectGui.DirectButton(text=('YES'),
                                            pos=(-.2,0,-0.3), scale=0.05, 
                                            command=self.endHandler, extraArgs=['YES'])
                no = DirectGui.DirectButton(text=('NO'),
                                            pos=(.2,0,-0.3), scale=0.05, 
                                            command=self.endHandler, extraArgs=['NO'])
            else:
                self.taskMgr.remove("keepTimer")
                self.timerP1Label.destroy()
                self.timerP2Label.destroy()
                
                goodGameText = OnscreenText(
                    text='Good Game!', pos = (0,-0.2), scale = .08)
                ok = DirectGui.DirectButton(text=('EXIT'),
                                            pos=(0,0,-0.3), scale=0.05, 
                                            command=self.endHandler, extraArgs=["NO"])

        return Task.cont


    def timerHandler(self, task):
        if self.player == self.myColor:
            minute = str(self.timerP1//60)
            second = str(self.timerP1%60)
            
            if len(minute) < 2:
                minute = '0' + minute
            if len(second) < 2:
                second = '0' + second

            self.timerP1Label.text = minute+':'+second
                
            self.timerP1 -= 1
            if self.timerP1 < 1 or (self.passedTime > 120 and self.player == self.myColor):
                # GAME OVER! TIMER RAN OUT
                self.taskMgr.add(self.gameOverCam, "END")
                self.end = True

                WINNER = ""

                if self.myColor == 'w':
                    mate = OnscreenText(text ='OUT OF TIME!', pos = (0,0.2), scale = .3)
                    textObject = OnscreenText(text ='BLACK WON THE GAME!', 
                            pos = (0,0), scale = .1)
                else:
                    mate = OnscreenText(text ='OUT OF TIME!', pos = (0,0.2), scale = .3)
                    textObject = OnscreenText(text ='WHITE WON THE GAME!', 
                            pos = (0,0), scale = .1)


                self.taskMgr.remove("keepTimer")
        else:
            minute = str(self.timerP2//60)
            second = str(self.timerP2%60)
            
            if len(minute) < 2:
                minute = '0' + minute
            if len(second) < 2:
                second = '0' + second

            self.timerP2Label.text = minute+':'+second
            self.timerP2 -= 1
            
            if self.timerP2 < 1 or (self.passedTime > 120 and self.player != self.myColor):
                # GAME OVER! TIMER RAN OUT
                self.taskMgr.add(self.gameOverCam, "END")
                self.end = True
                winner = ""
                if self.myColor == 'w':
                    mate = OnscreenText(text ='OUT OF TIME!', pos = (0,0.2), scale = .3)
                    textObject = OnscreenText(text ='WHITE WON THE GAME!', 
                            pos = (0,0), scale = .1)
                else:
                    mate = OnscreenText(text ='OUT OF TIME!', pos = (0,0.2), scale = .3)
                    textObject = OnscreenText(text ='BLACK WON THE GAME!', 
                            pos = (0,0), scale = .1)
    
                self.taskMgr.remove("keepTimer")

        if self.passedTime > 90:
            if self.player == self.myColor:
                temp = OnscreenText(
                        text = f'You have {120-self.passedTime} seconds to make a move.', 
                        pos = (0, 0.9), scale = .06)

                self.timer.append(6.5)
                whichTimer = len(self.timer)-1

                self.taskMgr.add(self.displayWarning, f"TIMERWARN{whichTimer}", 
                                    extraArgs=[f"TIMERWARN{whichTimer}", temp, whichTimer])

        self.passedTime += 1
        return Task.again


    def startTemporaryTimer(self, task):
        if len(self.Engine.moveLog) == 0:
            self.passedTime += 1
        else:
            self.taskMgr.remove(task)

        if self.passedTime > 10:
            temp = OnscreenText(
            text = f'You have {30-self.passedTime} seconds to make a move.', 
                        pos = (0, 0.9), scale = .06)

            self.timer.append(6.5)
            whichTimer = len(self.timer)-1

            self.taskMgr.add(self.displayWarning, f"FIRSTTIMERWARN{whichTimer}", 
                                extraArgs=[f"FIRSTTIMERWARN{whichTimer}", temp, whichTimer])

        if self.passedTime > 29:
            self.taskMgr.remove(task)
            self.chatConn.sendMessage(self.nameP2, "I Resign")

            if self.myColor == 'w':
                mate = OnscreenText(text = 'You Resigned.', pos = (0,0.2), scale = .3)
                textObject = OnscreenText(text = 'BLACK WON THE GAME!', 
                    pos = (0,0), scale = .1)
                self.taskMgr.add(self.gameOverCam, "END")
                self.end = True

                if (wins[0] + wins[1] + wins[2])%2 == 0:
                    wins[1] += 1
                else:
                    wins[0] += 1
        return Task.again


    def endHandler(self, ans):
        self.mySound.stop()
        if self.mode == 'Multiplayer':
            self.chatConn.sendMessage(self.nameP2, "I Quit.")

        if ans == "NO":
            playAgain = False

        taskMgr.stop()
        base.destroy()
                


    def displayWins(self, destroy=False):
        # Display current players
        colors = ["White", "Black"]
        allGames = wins[0] + wins[1] + wins[2]


        if not destroy:
            # Display curren players
            p1Color, p2Color = colors[allGames%2], colors[(allGames+1)%2]

            if self.mode == "Multiplayer":
                if self.myColor == 'w':
                    p1Color, p2Color = "White", "Black"
                else:
                    p1Color, p2Color = "Black", "White"


            self.plr1Color = OnscreenText(
                    text = f'{self.nameP1}: {p1Color}', 
                    pos = (-.5, -0.9), scale = .07)
            self.plr2Color = OnscreenText(
                    text = f'{self.nameP2}: {p2Color}', 
                    pos = (0.5, -0.9), scale = .07)
                

            if wins != [0, 0, 0]:
                # Make the scores appear
                self.plr1WinsText = OnscreenText(
                    text = f'Wins: {wins[0]}', pos = (-.5, -0.95), scale = .05)

                self.plr2WinsText = OnscreenText(
                    text = f'Wins: {wins[1]}', pos = (0.5, -0.95), scale = .05)

                self.drawsText = OnscreenText(
                    text = f'Draws: {wins[2]}', pos = (0, -0.95), scale = .05)

                if self.mode == "AI":
                    if allGames%2 == 1:
                        self.myColor = 'b'
                        self.AIToPlay = True
                        self.taskMgr.doMethodLater(.5, self.makeAIMove, "AIHandler")

                        self.view = 0
                        self.changeView()
                    else:
                        self.myColor = 'w'
                        self.AIToPlay = False

                        self.view = 2
                        self.changeView()     

        else:
            self.plr1Color.destroy()
            self.plr2Color.destroy()

            if self.mode == 'Multiplayer':
                self.resignButton.destroy()
                self.drawButton.destroy()
                self.undoButton.destroy()
            else:
                if allGames > 1:
                    self.plr1WinsText.destroy()
                    self.plr2WinsText.destroy()
                    self.drawsText.destroy()


class MainMenu():
    def __init__(self):
        self.top = tkinter.Tk()
        self.top.title("The Queen's Gambit")
        self.top.geometry('512x512+500+200')
        self.top.resizable(0,0)
        self.open = False
    
        
        # need canvas to load background image
        C = tkinter.Canvas()
        filename = tkinter.PhotoImage(file = PATH+"Textures/chessbg2.png")
        background_label = tkinter.Label(self.top, image=filename)
        background_label.place(x=0, y=0,relwidth=1, relheight=1)

        playOnlineButton = tkinter.Button(self.top, text='Play Online',
                                          command= lambda v='Online': self.mode(v))
        playAIButton = tkinter.Button(self.top, text='Play against AI',
                                      command = lambda v='AI': self.mode(v))

        playOnlineButton.place(relx = 0.3, rely = 0.35, anchor = tkinter.CENTER,
                               height=40, width=150)
        playAIButton.place(relx = 0.8, rely = 0.5, anchor = tkinter.CENTER,
                           height=40, width=150)
        C.pack()
        self.top.mainloop()


    def mode(self, v):
        # make sure user can't open multiple screens
        if not self.open:
            self.open = True
            if v == 'AI':
                self.top.destroy()
                AI = ChessAI()
                AI.play()
            else:
                online = Multiplayer(self)
                online.loginScreen()


class Multiplayer():

    def __init__(self, mainMenuObj):
        self.ChatCommObj = chatComm("86.36.46.10", 15112)
        self.mainMenuOpen = True

        self.lWnd = tkinter.Tk()
        self.lWnd.title('Login')
        self.lWnd.geometry("250x200+630+220")

        self.playingChess = []
        self.online = []
        self.myStatus = "Online"

        self.mainMenuObj = mainMenuObj
        self.mainMenu = mainMenuObj.top
        self.mainScreenHolder = ''
        self.mainuser = ''
        self.sentRequests = []
        self.requestsOpen = False

    '''
    IMPORTED CODE BELOW
    '''

    def isValidLogin(self, username, password):
        # calls the function login to see if this is correct
        ans = self.ChatCommObj.login(username, password)
        self.lWnd.destroy()
        self.mainMenuObj.open = False
        # if it is the correct login info, then go to the mainScreen
        if ans:
            self.mainuser = username
            self.mainScreen()

    def loginScreen(self):
        # set up window
        lWnd = self.lWnd
    

        # set up labels
        userLabel = tkinter.Label(lWnd, text='Username')
        userEntry = tkinter.Entry(lWnd)
        passLabel = tkinter.Label(lWnd, text='Password')
        passEntry = tkinter.Entry(lWnd,  show="*")
        okButton = tkinter.Button(lWnd, text='OK',
            command=lambda :self.isValidLogin(userEntry.get(), 
                passEntry.get()))

        # pack labels
        userLabel.pack()
        userEntry.pack()
        passLabel.pack()
        passEntry.pack()
        okButton.pack()

        # start loop for login window
        lWnd.protocol("WM_DELETE_WINDOW", lambda:self.onLogInClose())
        lWnd.mainloop()

    '''
    END OF IMPORTED CODE
    SOURCE: fmashhadhw8.py (15-122 Homework 8: Faisal Mashhadi)
    '''

    def onLogInClose(self):
        self.mainMenuObj.open = False
        self.lWnd.destroy()


    def updateStatus(self, friendsListOn, friendsListOff):
        # update friends list (online and offline)
        friends = self.ChatCommObj.getFriends()
        friendsListOn.delete(0, tkinter.END)
        friendsListOff.delete(0, tkinter.END)
        order = []

        for friend in friends:
            if friend != self.mainuser:
                if friend in self.online:
                    friendsListOn.insert(tkinter.END, friend)
                else:
                    friendsListOff.insert(tkinter.END, friend)


    def checkForMessages(self, mainScreen, friendsListOn, friendsListOff):
        newMessages, newFiles = self.ChatCommObj.getMail()
        update = False

        if newMessages != []:
            for u,m in newMessages:
                if m == "Are you online?":
                    self.ChatCommObj.sendMessage(u, f"Status: {self.myStatus}")

                if m[8:] == "Online":
                    if u not in self.online:
                        self.online.append(u)
                        update = True

                if m == "Going Offline!":
                    if u in self.online:
                        self.online.remove(u)
                        update = True

                if m == "Do you want to play Chess?":
                    if self.playingChess == []:
                        popUp = tkinter.messagebox.askquestion('Play Chess',
                                    f'Do you want to play Chess with {u}?')

                        if popUp == 'yes':
                            self.ChatCommObj.sendMessage(u, "Yes I want to play!")
                            self.playingChess.append(u)
                            self.setUpGame('w')

                        else:
                            self.ChatCommObj.sendMessage(u, "No I don't want to play.")

                            if u in self.sentRequests:
                                self.sentRequests.remove(u)

                if m == "Yes I want to play!":
                    if self.playingChess == [] and u in self.sentRequests:
                        self.sentRequests.remove(u)
                        self.playingChess.append(u)
                        self.setUpGame('b')

                elif m == "No I don't want to play.":
                    if u in self.sentRequests:
                        self.sentRequests.remove(u)
                        tkinter.messagebox.showinfo('Declined',
                                f'{u} has declined your request to play now.')
    
        
        if update or friendsListOff.size() == 0:
            self.updateStatus(friendsListOn, friendsListOff)
    
        mainScreen.after(3000, lambda: self.checkForMessages(mainScreen,
                                                             friendsListOn, friendsListOff))


    def playChess(self, friendList):
        if friendList.curselection():
            friend = friendList.get(friendList.curselection())
            friend = friend[friend.find(' ')+1:]
            print(friend)
            
            if friend in self.online:
                self.sentRequests.append(friend)
                self.ChatCommObj.sendMessage(friend, "Do you want to play Chess?")
                tkinter.messagebox.showinfo('Success!',
                    f'Request to play chess with {friend} has been sent successfully!')


    def addFriend(self, usersList, friendListOn, friendsListOff):
        if usersList.curselection():
            user = usersList.get(usersList.curselection())
            self.ChatCommObj.sendFriendRequest(user)

            tkinter.messagebox.showinfo('Success!',
                    f'Friend Request to {user} has been sent successfully!')

            self.ChatCommObj.sendMessage(user, "Are you online?")

            self.updateStatus(friendsListOn, friendsListOff)


    def viewRequests(self):
        if not self.requestsOpen:
            self.requestsOpen = True

            requests = self.ChatCommObj.getRequests()

            rWnd = tkinter.Toplevel(self.mainScreenHolder)
            rWnd.title("Friend Requests")

            requestsList = tkinter.Listbox(rWnd)

            for request in requests:
                requestsList.insert(tkinter.END, request)

            acceptButton = tkinter.Button(rWnd, text='Accept Friend',
                            command=lambda:self.acceptFriend(requestsList, rWnd))

            requestsList.pack()
            acceptButton.pack()

            rWnd.protocol("WM_DELETE_WINDOW", lambda: self.onRequestClosing(rWnd))


            
            
    def acceptFriend(self, requestsList, wnd):
        if requestsList.curselection():
            user = requestsList.get(requestsList.curselection())
            self.ChatCommObj.acceptFriendRequest(user)
            wnd.destroy()
            self.requestsOpen = False
            self.viewRequests()


    def onRequestClosing(self, wnd):
        self.requestsOpen = False
        wnd.destroy()
            
                

    def setUpGame(self, color):
        self.mainScreenHolder.destroy()
        game = Chess("Multiplayer", self.mainuser, 
            self.playingChess[0], color, self.ChatCommObj)
        game.run()

    
    def mainScreen(self):
        if self.mainMenuOpen:
            self.mainMenu.destroy()
            self.mainMenuOpen = False

        self.mainScreenHolder = tkinter.Tk()
        mainScreen = self.mainScreenHolder
        mainScreen.geometry('600x300+300+300')
        mainScreen.title("The Queen's Gambit")

        # set up labels
        allUsersLabel = tkinter.Label(mainScreen, text='All Users').grid(
            row=0, column=0)
        friendsLabelOnline = tkinter.Label(mainScreen,
            text='Your Friends (Online)').grid(
            row=0,column=1)
        friendsLabelOffline = tkinter.Label(mainScreen,
            text='Your Friends (Offline)').grid(
            row=0,column=2)

        # set up list box
        friends = self.ChatCommObj.getFriends()
        users = self.ChatCommObj.getUsers()
        friendsListOn = tkinter.Listbox(mainScreen)
        friendsListOff = tkinter.Listbox(mainScreen)
        allUsersList = tkinter.Listbox(mainScreen)

        for friend in friends:
            if friend == 'assertivethrush' or friend == 'fts':
                self.ChatCommObj.sendMessage(friend, "Are you online?")

        for user in users:
            allUsersList.insert(tkinter.END, user)

        # layout list boxes
        allUsersList.grid(row=1, column=0)
        friendsListOn.grid(row=1, column=1)
        friendsListOff.grid(row=1, column=2)

        self.checkForMessages(mainScreen, friendsListOn, friendsListOff)

        # Buttons
        addFriendButton = tkinter.Button(mainScreen, text='Add Friend',
                                         command=lambda:self.addFriend(
                                             allUsersList, friendsListOn, friendsListOff))
        playChessButton = tkinter.Button(mainScreen, text='Play Chess!',
                                         command=lambda:self.playChess(friendsListOn))
        viewRequestsButton = tkinter.Button(mainScreen, text='View Requests',
                                         command=lambda:self.viewRequests())

        playChessButton.grid(row=2, column=1)
        addFriendButton.grid(row=2, column=0)
        viewRequestsButton.grid(row=2, column=2)

        mainScreen.protocol("WM_DELETE_WINDOW", lambda:self.onClosing(mainScreen))
        
        mainScreen.mainloop()


    def onClosing(self, wnd):
        for friend in self.online:
            self.ChatCommObj.sendMessage(friend, "Going Offline!")

        wnd.destroy()  
        


wins = [0, 0, 0]
playAgain = True
class ChessAI():
    def play(self):
        while playAgain:
            if (wins[0]+wins[1]+wins[2])%2 == 0:
                game = Chess("AI", "Player 1", "Computer", "w")
            else:
                game = Chess("AI", "Player 1", "Computer", "b")

            game.run()

            if not playAgain:
                sys.exit()

mainMenu = MainMenu()
sys.exit()
