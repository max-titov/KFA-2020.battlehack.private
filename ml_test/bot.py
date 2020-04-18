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
	global row,col
	row, col = get_location()

	first_layer = []
	if team == Team.WHITE:
		for i in range(-sensor_radius, sensor_radius+1):
			for j in range(-sensor_radius, sensor_radius+1):
				if i == 0 and j == 0:
					



	if check_right(): # up and right
		capture_right()

	elif check_left(): # up and left
		capture_left()

	# otherwise try to move forward
	elif can_move_forward() and (equal_trade_if_move() or close_to_enemy_side()):
		#if row < whiteHalfway:
		move_forward()
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


def overlord_turn():
	board = get_board()
	
	allied_list = []
	enemy_list = []

	for tempCol in range(board_size):
		for tempRow in range(board_size):
			temp = board[tempCol][tempRow]
			if temp == opp_team:
				allied_list.append(0)
				enemy_list.append(1)
			elif temp == team:
				allied_list.append(1)
				enemy_list.append(0)
			else:
				allied_list.append(0)
				enemy_list.append(0)



	# for _ in range(board_size):
	# 	i = random.randint(0, board_size - 1)
	# 	if not check_space(backRow, i):
	# 		spawn(backRow, i)
	# 		break

# python -i run.py ml_test weights --raw-text
