import random


# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

board_size = 16
team = None
opp_team = None
robottype = None

#PAWN

forward = 0


#OVERLORD

spawnRow = 0




DEBUG = 1
def dlog(str):
	if DEBUG > 0:
		log(str)


def check_space_wrapper(r, c, board_size):
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
	global board_size, team, opp_team, robottype

	board_size = get_board_size()

	team = get_team()
	opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
	dlog('Team: ' + str(team))

	robottype = get_type()
	dlog('Type: ' + str(robottype))

	if robottype == RobotType.PAWN:
		pawn_init()
	else:
		overlord_init()

##############################################################
############################ PAWN ############################
##############################################################

def pawn_init():
	global forward

	if team == Team.WHITE:
		forward = 1
	else:
		forward = -1

def pawn_turn():
	row, col = get_location()
	dlog('My location is: ' + str(row) + ' ' + str(col))

	if team == Team.WHITE:
		forward = 1
	else:
		forward = -1

	# try catpuring pieces
	if check_space_wrapper(row + forward, col + 1, board_size) == opp_team: # up and right
		capture(row + forward, col + 1)
		dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

	elif check_space_wrapper(row + forward, col - 1, board_size) == opp_team: # up and left
		capture(row + forward, col - 1)
		dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

	# otherwise try to move forward
	elif row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col, board_size):
		#               ^  not off the board    ^            and    ^ directly forward is empty
		move_forward()
		dlog('Moved forward!')

	confusion = "you need a line here to avoid segfault. we aren't sure why but are working on it"
	# ^ I think this is related to the potential ambiguity of what the following else is referring to?

##############################################################
########################## OVERLORD ##########################
##############################################################

def overlord_init():
	global spawnRow
	if team == Team.WHITE:
		spawnRow = 0
	else:
		spawnRow = board_size - 1

def overlord_turn():
	for _ in range(board_size):
		i = random.randint(0, board_size - 1)
		if not check_space(spawnRow, i):
			spawn(spawnRow, i)
			dlog('Spawned unit at: (' + str(spawnRow) + ', ' + str(i) + ')')
			break