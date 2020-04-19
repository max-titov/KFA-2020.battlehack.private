import random


# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

board_size = 16
team = None
opp_team = None
robottype = None
backRow = 0

#PAWN

sensor_radius = 2

#OVERLORD

sameRowAlliedPawnWeight = -64
adjacentRowAlliedPawnWeight = 0

sameRowEnemyPawnWeight = 16
adjacentRowEnemyPawnWeight = 16

sameRowAlliedPawnDistanceMultiplier = 1
adjacentRowAlliedPawnDistanceMultiplier = 0

sameRowEnemyPawnDistanceMultiplier = -1
adjacentRowEnemyPawnDistanceMultiplier = -1

enemyOneTileAwayWeight = 1000
enemyTwoTilesAwayWeight = 700
enemyOneAdjacentTileAwayWeight = -500

DEBUG = 1
def dlog(str):
	if DEBUG > 0:
		log(str)


def check_space_wrapper(r, c):
	# check space, except doesn't hit you with game errors
	if r < 0 or c < 0 or c >= board_size or r >= board_size:
		return False
	try:
		return check_space(r, c)
	except:
		return None

def turn():
	f = open("test.txt","r")
	contents = f.read()
	dlog(contents)

	if robottype is None:
		init()

	if robottype == RobotType.PAWN:
		pawn_turn()
	else:
		overlord_turn()

	bytecode = get_bytecode()
	dlog('Done! Bytecode left: ' + str(bytecode))

def init():
	global board_size, team, opp_team, robottype, backRow, forward

	board_size = get_board_size()

	team = get_team()

	robottype = get_type()

	if team == Team.WHITE:
		backRow = 0
		forward = 1
		opp_team = Team.BLACK
	else:
		backRow = board_size - 1
		forward = -1
		opp_team = Team.WHITE

	if robottype == RobotType.PAWN:
		pawn_init()
	else:
		overlord_init()

##############################################################
############################ PAWN ############################
##############################################################

def pawn_init():
	return

def check_right():
	return check_space_wrapper(row + forward, col + 1) == opp_team

def check_left():
	return check_space_wrapper(row + forward, col - 1) == opp_team

def check_right2():
	return check_space_wrapper(row + forward*2, col + 1) == opp_team

def check_left2():
	return check_space_wrapper(row + forward*2, col - 1) == opp_team

def check_right_adjacent_ally():
	return check_space_wrapper(row, col + 1) == team

def check_left_adjacent_ally():
	return check_space_wrapper(row, col - 1) == team

def capture_right():
	capture(row + forward, col + 1)

def capture_left():
	capture(row + forward, col - 1)

def can_move_forward():
	return row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col)

def close_to_enemy_side():
	distance = abs(row-backRow)
	return distance >= board_size-3

def pawn_turn():
	#global row,col
	row, col = get_location()

	first_layer = []
	if team == Team.WHITE:
		for i in range(-sensor_radius, sensor_radius+1):
			for j in range(-sensor_radius, sensor_radius+1):
				if i == 0 and j == 0:
					continue
				pawn = check_space_wrapper(row+i, col+j)
				if pawn == team:
					first_layer.append(1)
					first_layer.append(0)
					first_layer.append(0)
				elif pawn == opp_team:
					first_layer.append(0)
					first_layer.append(1)
					first_layer.append(0)
				else:
					first_layer.append(0)
					first_layer.append(0)
					first_layer.append(1)
		first_layer.append(row)
		first_layer.append(col)
		if col == 0 or col == 15:
			first_layer.append(1)
		else:
			first_layer.append(0)


	test_weights = [[random.randint(0,10) for x in range(75)] for y in range(20)]
	test_bias = [random.randint(0,10) for x in range(20)]
	second_layer = []

	second_layer_len = 20

	for i in range(second_layer_len):
		value = test_bias[i]
		for j in range(len(first_layer)):
			value += first_layer[j] * test_weights[i][j]
		second_layer.append(value)
	dlog('Second layer values: ' + str(second_layer))

	#third layer
	second_weights = [[random.randint(0,10) for x in range(20)] for y in range(2)]
	second_bias = [random.randint(0,10) for x in range(2)]
	output_layer = []
	output_layer_len = 2
	for i in range(output_layer_len):
		tempValue = second_bias[i]
		for j in range(second_layer_len):
			tempValue += second_layer[j] * second_weights[i][j]
		output_layer.append(value)
	dlog('Output layer values: ' + str(output_layer))

	#if check_right(): # up and right
		#capture_right()

	#elif check_left(): # up and left
		#capture_left()

	# otherwise try to move forward
	#elif can_move_forward():
		#if row < whiteHalfway:
		#move_forward()
	confusion = "you need a line here to avoid segfault. we aren't sure why but are working on it"
	# ^ I think this is related to the potential ambiguity of what the following else is referring to?

##############################################################
########################## OVERLORD ##########################
##############################################################

def overlord_init():
	global backRow
	if team == Team.WHITE:
		backRow = 0
	else:
		backRow = board_size - 1


def spawn_weights(board): # TODO: add adjecent col to weight value
	weights = []
	for tempCol in range(board_size):
		weights.append(0)

		#check same col
		for tempRow in range(board_size):
			pawn = board[tempRow][tempCol]
			if pawn != None: # there is a pawn
				distance = abs(tempRow-backRow) # distance to pawn from your back row
				if pawn == team: # your pawn
					weights[tempCol] = weights[tempCol] + sameRowAlliedPawnWeight + sameRowAlliedPawnDistanceMultiplier * distance
				else: # enemy pawn
					weights[tempCol] = weights[tempCol] + sameRowEnemyPawnWeight + sameRowEnemyPawnDistanceMultiplier * distance

		#check left adjacent col
		if tempCol > 0:
			for tempRow in range(board_size):
				pawn = board[tempRow][tempCol-1]
				if pawn != None: # there is a pawn
					distance = abs(tempRow-backRow) # distance to pawn from your back row
					if pawn == team: # your pawn
						weights[tempCol] = weights[tempCol] + adjacentRowAlliedPawnWeight + adjacentRowAlliedPawnDistanceMultiplier * distance
					else: # enemy pawn
						weights[tempCol] = weights[tempCol] + adjacentRowEnemyPawnWeight + adjacentRowEnemyPawnDistanceMultiplier * distance

		#check right adjacent col
		if tempCol < board_size-1:
			for tempRow in range(board_size):
				pawn = board[tempRow][tempCol+1]
				if pawn != None: # there is a pawn
					distance = abs(tempRow-backRow) # distance to pawn from your back row
					if pawn == team: # your pawn
						weights[tempCol] = weights[tempCol] + adjacentRowAlliedPawnWeight + adjacentRowAlliedPawnDistanceMultiplier * distance
					else: # enemy pawn
						weights[tempCol] = weights[tempCol] + adjacentRowEnemyPawnWeight + adjacentRowEnemyPawnDistanceMultiplier * distance
		
		if board[backRow+forward][tempCol] == opp_team: # if opponent pawn is one tile away from back row
			weights[tempCol] = weights[tempCol] + enemyOneTileAwayWeight 
		
		if board[backRow+forward*2][tempCol] == opp_team: # if opponent pawn is two tiles away from back row
			weights[tempCol] = weights[tempCol] + enemyTwoTilesAwayWeight 

		if tempCol > 0 and board[backRow+forward][tempCol-1] == opp_team: # if opponent pawn is one tile away from back row and one to the left:
			weights[tempCol] = weights[tempCol] + enemyOneAdjacentTileAwayWeight

		if tempCol < board_size-1 and board[backRow+forward][tempCol+1] == opp_team: # if opponent pawn is one tile away from back row and one to the right:
			weights[tempCol] = weights[tempCol] + enemyOneAdjacentTileAwayWeight

	return weights

def maxIndex(list):
	maxNum = list[0]
	maxIndex = 0
	for i in range(len(list)):
		if list[i] > maxNum:
			maxIndex = i
			maxNum = list[i]
	return maxIndex

def overlord_turn():
	board = get_board()
	weights = spawn_weights(board)
	
	debug = ''
	for i in range(board_size):
		debug = debug + str(weights[i]) + ' '
	dlog(debug)

	for i in range(board_size):
		maxWeightCol = maxIndex(weights)
		if not check_space(backRow, maxWeightCol):
			spawn(backRow, maxWeightCol)
			break
		else:
			weights[maxWeightCol] = -100000

	# for tempCol in range(board_size):
	# 	for tempRow in range(board_size):
	# 		temp = board[tempCol][tempRow]
	# 		if temp == opp_team:
	# 			allied_list.append(0)
	# 			enemy_list.append(1)
	# 		elif temp == team:
	# 			allied_list.append(1)
	# 			enemy_list.append(0)
	# 		else:
	# 			allied_list.append(0)
	# 			enemy_list.append(0)



	# for _ in range(board_size):
	# 	i = random.randint(0, board_size - 1)
	# 	if not check_space(backRow, i):
	# 		spawn(backRow, i)
	# 		break

# python -i run.py ml_test weights --raw-text
