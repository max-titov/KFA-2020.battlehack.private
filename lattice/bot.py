import random

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

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

latticeRow = 0
maxRows = 25
buildCol = 0

def turn():
    global latticeRow, maxRows, buildCol
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    dlog('Starting Turn!')
    board_size = get_board_size()

    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    dlog('Team: ' + str(team))

    robottype = get_type()
    dlog('Type: ' + str(robottype))

    if robottype == RobotType.PAWN:
        row, col = get_location()
        dlog('My location is: ' + str(row) + ' ' + str(col))

        if team == Team.WHITE:
            forward = 1
        else:
            forward = -1

        #A type designation of 0 means it is even; 1 means it is odd    
        typeDesignation = 3
        if col%2 == 0:
            typeDesignation = 0
        else:
            typeDesignation = 1
        surroundings = sense()

        # try capturing pieces
        if check_space_wrapper(row + forward, col + 1, board_size) == opp_team: # up and right
            capture(row + forward, col + 1)
            dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

        elif check_space_wrapper(row + forward, col - 1, board_size) == opp_team: # up and left
            capture(row + forward, col - 1)
            dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

        """# otherwise try to move forward
        elif row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col, board_size):
            #               ^  not off the board    ^            and    ^ directly forward is empty
            #move_forward()
            dlog('Moved forward!')
        """
        #dlog('2D dimensions: ' + str(len(surroundings))+', '+str(len(surroundings[0])))
        #Three forward movement conditions: piece behind, out of line of the lattice, and next to wall
        coords = [row, col]
        if checkMoveConditions(typeDesignation, team, coords):
            move_forward()
            dlog('Moved forward')
        confusion = "you need a line here to avoid segfault. we aren't sure why but are working on it"
        # ^ I think this is related to the potential ambiguity of what the following else is referring to?

    else:
        if team == Team.WHITE:
            index = 0
        else:
            index = board_size - 1
        
            if latticeRow < maxRows:
                if not check_space(index, buildCol):
                    spawn(index, buildCol)
                    dlog('Spawned unit at: (' + str(index) + ', ' + str(buildCol) + ')')
                buildCol += 2
                dlog('buidCol value:' + str(buildCol))
                if buildCol > 15:
                    dlog('latticeRow value:' + str(latticeRow))
                    latticeRow+=1
                    if latticeRow%2==0:
                        buildCol = 0
                    else:
                        buildCol = 1


            """for _ in range(board_size):
                i = random.randint(0, board_size - 1)
                if not check_space(index, i):
                    spawn(index, i)
                    dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
                    break"""

        bytecode = get_bytecode()
        dlog('Done! Bytecode left: ' + str(bytecode))

#Something behind, out of the lattice, next to wall
def checkMoveConditions(typeD, team, coords):
    row, col = coords[0], coords[1]
    if team == Team.BLACK:
        if row == 15:
            return True
        elif typeD%2 != row%2:
            return True
        elif check_space(row+1, col):
            return True
    
    elif team == Team.WHITE:
        if row == 0:
            return True
        elif typeD%2 != row%2:
            return True
        elif check_space(row-1, col):
            return True
    return False
#Run command:
#python viewer.py nathan nathan
#python -i run.py nathan nathan --raw-text