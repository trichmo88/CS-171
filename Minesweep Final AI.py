# ==============================CS-199==================================
# FILE:			MyAI.py
#
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random



class singleTile():
	def __init__(self, row, col, rowDimension, colDimension):
		self.X = row											# X position of the tile
		self.Y = col											# Y position of the tile
		self.state = -2											# States: -2 = ??, -1 = flag/mine, num = num (LOL) 
		self.surroundingTiles = 8								# Keeps track of how many tiles surround this one
		
		if (self.X == 0) or (self.X == rowDimension - 1):		# Tile is on the first row, 3 less than normal
			self.surroundingTiles = self.surroundingTiles - 3
		if (self.Y == 0) or (self.Y == colDimension - 1):		# Tile is on the first col, 3 less than normal
			self.surroundingTiles = self.surroundingTiles - 3
		if self.surroundingTiles == 2:							# Tile is a corner edge, corrected to 3 not 2
			self.surroundingTiles = 3


	def uncoverTile(self, number):		# Uncovers tile and modifies its status
		self.state = number


	def setFlag(self) -> None:			# Sets the tile to be a flag
		self.state = -1




class MyAI( AI ):
	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		
		self.rows 			= colDimension
		self.cols 			= rowDimension
		self.totalMines 	= totalMines
		self.prevMove 		= Action(AI.Action.UNCOVER,startX,startY)
		self.startTile		= (startX,startY)
		
		self.board 			= [] 
		self.revealedTiles 	= []
		self.stillInTiles	= [] 
		self.surrUnknown 	= []

		for r in range(self.rows):
			temp = []
			for c in range(self.cols):
				temp.append(singleTile(r, c, self.rows, self.cols))
			self.board.append(temp)

		#print("Starting at: (" + str(startX) + "," + str(startY) + ")")
		#print("Dimensions: (" + str(self.rows) + "," + str(self.cols) + ") <-(RxC)")
		#print("Total Mines:", self.totalMines)
		#for r in self.board:
		#	print(r)
		#	for c in r:
		#		print(c.state)
		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
	
	def canSolve(self, uncovStmts):
		if len(uncovStmts[0]) == 0: 
			return False
		if uncovStmts[1] == 0 or len(uncovStmts[0]) == uncovStmts[1]:
			return True
		
		return False
	
	
	def addToStillIn(self, stmts):
		for s in stmts:
			if s[0] == 0:
				for tile in s[0]:
					self.stillInTiles.append( Action(AI.Action.UNCOVER, tile.X, tile.Y) )
			elif len(s[0]) == s[1]:
				for tile in s[0]:
					self.stillInTiles.append( Action(AI.Action.FLAG, tile.X, tile.Y) )
					
	
	def takeOut(self, s1, s2):
		temp = True
		
		for tile in s1[0]:
			if tile not in s2[0]:
				temp = False
				break
		
		if temp == True:
			results = [[], 0]
			
			for tile in s2[0]:
				if tile not in s1[0]:
					results[0].append(tile)
					
			results[1] = s2[1] - s1[1]
			return results
		
		return 
		
	
	def statementForLoop(self, trueStmts, solvableStmts, keepGoing):
		stm_list = []

		for x in trueStmts:
			for y in trueStmts:
				if x != y:
					newStmt = self.takeOut(x, y)
					
					if newStmt != None:
						temp = self.canSolve(newStmt)
						
						if temp:
							if newStmt not in solvableStmts:
								solvableStmts.append(newStmt)
						else:
							if newStmt not in stm_list and newStmt not in trueStmts:
								stm_list.append(newStmt)
								keepGoing = True
								
		return stm_list
	
	
	def solveKB(self, trueStmts, solvableStmts):
		keepGoing = True
		
		while keepGoing:
			keepGoing = False
			stm_list = self.statementForLoop(trueStmts, solvableStmts, keepGoing)					
			trueStmts.extend(stm_list)
		
		self.addToStillIn(solvableStmts)
		
					
	def transferFromBoard(self):
		mines = 0
		uStmts = [[], 0] 		# [0] = tile list, [1] = mines

		for _,l in enumerate(self.board):
			for _,tile in enumerate(l):
				if tile.state == -2:
					uStmts[0].append(tile)
				elif tile.state == -1:
					mines = mines + 1
				
		uStmts[1] = self.totalMines - mines
		return mines, uStmts
	
	
	def transferFromUnknown(self, trueStmts):
		for tile in self.surrUnknown:
			if tile.state >= 0:
				surrMines = 0
				uStmts = [[],0]
				
				tile_list = self.getSurroundingTiles(tile.X, tile.Y)
				
				for t in tile_list:
					if t.state==-2:
						uStmts[0].append(t)
					elif t.state==-1:
						surrMines = surrMines + 1
						
				uStmts[1] = tile.state-surrMines
				
				if uStmts not in trueStmts:
					trueStmts.append(uStmts)
					
		
	def attemptLogic(self) -> None:
		trueStmts 		= []
		solvableStmts 	= []
		mines, uncovStmts = self.transferFromBoard()
		
		if uncovStmts[1] <= 5:	
			trueStmts.append(uncovStmts)
		
		#print("Attempting Logic (KB): ")
		#print("True Statements:", trueStmts)
		#print("Solvable Stmts: ", solvableStmts)
		#print("Mines: ", mines)
		#print("uncovStmts:", uncovStmts)
		
		self.transferFromUnknown(trueStmts)
		#print(trueStmts)
		
		self.solveKB(trueStmts, solvableStmts)
					
					
	
	def getSurroundingTiles(self, X, Y) -> list:
		tileList = []
		
		for a in range(-1, 2):
			for b in range(-1, 2):
				if a == 0 and b == 0:
					continue
				currX = X + a
				currY = Y + b
				if (currX >= 0 and currX < self.rows) and (currY >= 0 and currY < self.cols):
					tileList.append(self.board[currX][currY])
					
		return tileList
	
	
	def getTileInfo(self, tile_list):
		surrMines 		= 0
		notKnownTiles 	= 0
		notSolvedList 	= []
		
		for tile in tile_list:
			if tile.state == -2:
				notSolvedList.append(tile)
			elif tile.state == -1:
				surrMines += 1
			elif tile.state >= 0:
				notKnownTiles += 1
			else:
				return 
		
		return surrMines, notKnownTiles, notSolvedList
		
		
	def tileIsSolved(self, tile):
		self.surrUnknown.remove(tile)
		self.revealedTiles.append(tile)

					
	def tileIsSolvable(self, list, state):
		for tile in list:
			if state == 1:
				move = Action(AI.Action.UNCOVER, tile.X, tile.Y)
			elif state == 0:
				move = Action(AI.Action.FLAG, tile.X, tile.Y)
			alreadyIn = False
			
			for t in self.stillInTiles:
				if t.getX() == tile.X and t.getY() == tile.Y:
					alreadyIn = True
				
			if alreadyIn == False:
				self.stillInTiles.append(move)

	
	def solveTheTile(self, tile, surrTiles) -> None:
		surrMines, notKnownTiles, notSolvedList = self.getTileInfo(surrTiles)
		
		if surrMines + notKnownTiles == tile.surroundingTiles:
			self.tileIsSolved(tile)
		if surrMines==tile.state:							
			self.tileIsSolvable(notSolvedList, 1)			# 1 = uncover the tiles
		if len(notSolvedList) == tile.state-surrMines:		
			self.tileIsSolvable(notSolvedList, 0)			# 0 = flag the tiles
					
	
	def attemptToSolve(self):
		for tile in self.surrUnknown:
			#print("Current Tile: (" + str(tile.X) + "," + str(tile.Y) + ")")
			if tile.state != -2 and tile.state != -1:
				surrTiles = self.getSurroundingTiles(tile.X, tile.Y)
				#print("\t Surrounding Tiles", surrTiles)
				self.solveTheTile(tile, surrTiles)


	def guessBest(self):
		unknownTiles = [self.startTile]
		
		for r in range(self.rows):
			for c in range(self.cols):
				if self.board[r][c].state == -2:
					unknownTiles.append( (r,c) )

		x, y = random.choice(unknownTiles)
		#print("Guessing: (" + str(x) + "," + str(y) + ")")
		move = Action(AI.Action.UNCOVER, x, y)
		self.stillInTiles.append(move)	
		
	
	def getAction(self, number: int) -> "Action Object":
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		
		x = self.prevMove.getX()
		y = self.prevMove.getY()
		
		# print(" ~~~~~~~~~~~~~~~~~~~~~~  (" + str(x) + "," + str(y) + ") ~~~~~~~~~~~~~~~~~~~~~~ ")		
		
		if 0 <= number:
			self.board[x][y].uncoverTile(number)
			
			if ((self.board[x][y] in self.surrUnknown) == False) and ((self.board[x][y] in self.revealedTiles) == False):
				self.surrUnknown.append(self.board[x][y])
			
			#print("SurrUnknown: (len=" + str(len(self.surrUnknown)) + ")", self.surrUnknown)
		else:
			self.board[x][y].setFlag()
			#print("Sate:", self.board[x][y].state, " (Should be = -1)")


		self.attemptToSolve()													# First attempt to solve	
		# print("SillInTiles: (len=" + str(len(self.stillInTiles)) + ")", self.stillInTiles)
		 
		if len(self.stillInTiles) == 0:											# Attempt to logically solve if yet to find a tile
			self.attemptLogic()
			#print("\t 2nd Attempt:(len=" + str(len(self.stillInTiles)) + ")", self.stillInTiles)

			if len(self.stillInTiles) == 0:										# Last attempt: guess a tile and hope for the best
				self.guessBest()
				#print("\t\t 3rd Attempt:(len=" + str(len(self.stillInTiles)) + ")", self.stillInTiles)

		self.prevMove = self.stillInTiles.pop()
		#print("PrevMove: (" + str(self.prevMove.getX()) + "," + str(self.prevMove.getY()) + ")")
		return self.prevMove

		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
