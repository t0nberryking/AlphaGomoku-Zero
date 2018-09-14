import numpy as np
import logging
from itertools import chain

class Game:

	def __init__(self):		
		self.currentPlayer = 1
		self.gameState = GameState(np.zeros(225, dtype=np.int), 1)
		self.actionSpace = np.zeros(225, dtype=np.int)
		self.pieces = {'1':'X', '0': '-', '-1':'O'}
		self.grid_shape = (15,15)
		self.input_shape = (2,15,15)
		self.name = 'gomoku'
		self.state_size = len(self.gameState.binary)
		self.action_size = len(self.actionSpace)

	def reset(self):
		self.gameState = GameState(np.zeros(225, dtype=np.int), 1)
		self.currentPlayer = 1
		return self.gameState

	def step(self, action):
		next_state, value, done = self.gameState.takeAction(action)
		self.gameState = next_state
		self.currentPlayer = -self.currentPlayer
		info = None
		return ((next_state, value, done, info))

	def identities(self, state, actionValues):
		identities = [(state,actionValues)]

		currentBoard = state.board #do we need to turn this into an array?
		currentAV = actionValues   #do we need to turn this into an array?

		# currentBoard = np.array([
		# 	  currentBoard[6], currentBoard[5],currentBoard[4], currentBoard[3], currentBoard[2], currentBoard[1], currentBoard[0]
		# 	, currentBoard[13], currentBoard[12],currentBoard[11], currentBoard[10], currentBoard[9], currentBoard[8], currentBoard[7]
		# 	, currentBoard[20], currentBoard[19],currentBoard[18], currentBoard[17], currentBoard[16], currentBoard[15], currentBoard[14]
		# 	, currentBoard[27], currentBoard[26],currentBoard[25], currentBoard[24], currentBoard[23], currentBoard[22], currentBoard[21]
		# 	, currentBoard[34], currentBoard[33],currentBoard[32], currentBoard[31], currentBoard[30], currentBoard[29], currentBoard[28]
		# 	, currentBoard[41], currentBoard[40],currentBoard[39], currentBoard[38], currentBoard[37], currentBoard[36], currentBoard[35]
		# 	])

		# currentAV = np.array([
		# 	currentAV[6], currentAV[5],currentAV[4], currentAV[3], currentAV[2], currentAV[1], currentAV[0]
		# 	, currentAV[13], currentAV[12],currentAV[11], currentAV[10], currentAV[9], currentAV[8], currentAV[7]
		# 	, currentAV[20], currentAV[19],currentAV[18], currentAV[17], currentAV[16], currentAV[15], currentAV[14]
		# 	, currentAV[27], currentAV[26],currentAV[25], currentAV[24], currentAV[23], currentAV[22], currentAV[21]
		# 	, currentAV[34], currentAV[33],currentAV[32], currentAV[31], currentAV[30], currentAV[29], currentAV[28]
		# 	, currentAV[41], currentAV[40],currentAV[39], currentAV[38], currentAV[37], currentAV[36], currentAV[35]
		# 			])

		identities.append((GameState(currentBoard, state.playerTurn), currentAV))

		return identities


class GameState():
	def __init__(self, board, playerTurn):
		self.board = board
		self.pieces = {'1':'X', '0': '-', '-1':'O'}

		horizontal_wins = [[[x for x in range(start, start+5)] for start in range(row,row+11)] for row in range(0,225,15)]
		vertical_wins = [[[x for x in range(start, start+(5*15), 15)] for start in range(row,row+15)] for row in range(0,165,15)]
		left_diag_right_wins  = [[[x for x in range(left,left+(5*16),16)] for left in range(row,row+11)] for row in range(0,160,15)]
		right_diag_left_wins = [[[x for x in range(right,right+(5*14),14)] for right in range(row,row+11)] for row in range(4,160,15)]
		winners = []
		for wins in [horizontal_wins, vertical_wins, left_diag_right_wins, right_diag_left_wins]:
    		for items in list(chain.from_iterable(wins)):
        		winners.append(items)
		self.winners = winners

		self.playerTurn = playerTurn
		self.binary = self._binary()
		self.id = self._convertStateToId()
		# self.allowedActions = self._allowedActions() ## Not required 
		self.isEndGame = self._checkForEndGame()
		self.value = self._getValue()
		self.score = self._getScore()

	# def _allowedActions(self):
	# 	allowed = []
	# 	for i in range(len(self.board)):
	# 		if i >= len(self.board) - 7:
	# 			if self.board[i]==0:
	# 				allowed.append(i)
	# 		else:
	# 			if self.board[i] == 0 and self.board[i+7] != 0:
	# 				allowed.append(i)

	# 	return allowed

	def _binary(self):

		currentplayer_position = np.zeros(len(self.board), dtype=np.int)
		currentplayer_position[self.board==self.playerTurn] = 1

		other_position = np.zeros(len(self.board), dtype=np.int)
		other_position[self.board==-self.playerTurn] = 1

		position = np.append(currentplayer_position,other_position)

		return (position)

	def _convertStateToId(self):
		player1_position = np.zeros(len(self.board), dtype=np.int)
		player1_position[self.board==1] = 1

		other_position = np.zeros(len(self.board), dtype=np.int)
		other_position[self.board==-1] = 1

		position = np.append(player1_position,other_position)

		id = ''.join(map(str,position))

		return id

	def _checkForEndGame(self):
		if np.count_nonzero(self.board) == 225:
			return 1

		for x,y,z,a,b in self.winners:
			if (self.board[x] + self.board[y] + self.board[z] + self.board[a] + self.board[b] == 5 * -self.playerTurn):
				return 1
		return 0


	def _getValue(self):
		# This is the value of the state for the current player
		# i.e. if the previous player played a winning move, you lose
		for x,y,z,a,b in self.winners:
			if (self.board[x] + self.board[y] + self.board[z] + self.board[a] + self.board[b] == 5 * -self.playerTurn):
				return (-1, -1, 1)
		return (0, 0, 0)


	def _getScore(self):
		tmp = self.value
		return (tmp[1], tmp[2])




	def takeAction(self, action):
		newBoard = np.array(self.board)
		newBoard[action]=self.playerTurn
		
		newState = GameState(newBoard, -self.playerTurn)

		value = 0
		done = 0

		if newState.isEndGame:
			value = newState.value[0]
			done = 1

		return (newState, value, done) 




	def render(self, logger):
		for r in range(15):
			#logger.info([self.pieces[str(x)] for x in self.board[7*r : (7*r + 7)]])
			logger.info([self.pieces[str(x)] for x in self.board[15*r : (15*r+15)]])
		logger.info('--------------')



