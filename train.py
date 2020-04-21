import time
import argparse
import faulthandler
import sys
import threading
import random
import numpy as np

from battlehack20 import CodeContainer, Game, BasicViewer, GameConstants
from battlehack20.engine.game.team import Team

population_size = 120

input_count = 75
hidden_count = 20
output_count = 2

pawn_bias_L1 = np.zeros([population_size, hidden_count, input_count]).tolist()
pawn_weights_L1 = np.zeros([population_size, hidden_count, input_count]).tolist()
pawn_bias_L2 = np.zeros([population_size, output_count, hidden_count]).tolist()
pawn_weights_L2 = np.zeros([population_size, output_count, hidden_count]).tolist()

weight_zones = 3 # on border, one away from border, all other cases
board_size = 16

overlord_weights_same_allied = np.zeros([population_size, weight_zones, board_size]).tolist()
overlord_weights_adjacent_allied = np.zeros([population_size, weight_zones, board_size]).tolist()
overlord_weights_same_enemy = np.zeros([population_size, weight_zones, board_size]).tolist()
overlord_weights_adjacent_enemy = np.zeros([population_size, weight_zones, board_size]).tolist()

#Point values for each subsequent row from the board end:
point_values_list = [75, 25, 15, 10, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1]
penalty_values_list = [50, 15, 10, 5, 3, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

#Example bots list
example_bots_list = [['bot id', 84], ['bot id2', 56], ['bot id3', 10]]

fitnesses = np.zeros([population_size])

matchups_per_bot = 2

# BOT CODE IS BELOW #

sameRowAlliedWeights = [
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49], #on border
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49], #one away from boarder
[-64,-63,-62,-61,-60,-59,-58,-57,-56,-55,-54,-53,-52,-51,-50,-49]] #all other possibilities

sameRowEnemyWeights = [
[1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[1000,700,14,13,12,11,10,9,8,7,6,5,4,3,2,1]]

adjacentRowAlliedWeights = [
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

adjacentRowEnemyWeights = [
[-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1],
[-500,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]]

DEBUG = 1
def dlog(str):
    if DEBUG > 0:
        print(str)

def check_space_wrapper(game, bot, r, c, board_size):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return False
    try:
        return game.pawn_check_space(bot, r, c)
    except:
        return None

def dist_to_side(column, board_size):
    dist1 = column
    dist2 = board_size-1-column
    return dist1 if dist1 < dist2 else dist2

def check_right(game,bot,board_size,opp_team, row, col):
    return check_space_wrapper(game, bot, row + forward, col + 1, board_size) == opp_team

def check_left(game,bot,board_size,opp_team, row, col):
    return check_space_wrapper(game, bot, row + forward, col - 1, board_size) == opp_team

def capture_right(game, bot, row, col):
    game.capture(bot, row + forward, col + 1)

def capture_left(game, bot, row, col):
    game.capture(bot, row + forward, col - 1)

def can_move_forward(game,bot,board_size, row, col):
    return row + forward != -1 and row + forward != board_size and not check_space_wrapper(game, bot, row + forward, col, board_size)

def pawn_turn(game,bot,bot_num):
    board_size = game.get_board_size()

    team = game.get_team(bot)

    sensor_radius = 2

    if team == Team.WHITE:
        backRow = 0
        forward = 1
        opp_team = Team.BLACK
    else:
        backRow = board_size - 1
        forward = -1
        opp_team = Team.WHITE

    row, col = game.get_location(bot)

    first_layer = []
    if team == Team.WHITE:
        for i in range(-sensor_radius, sensor_radius+1):
            to_print = ""
            for j in range(-sensor_radius, sensor_radius+1):
                if i == 0 and j == 0:
                    continue
                pawn = check_space_wrapper(game, bot, row+i, col+j, board_size)
                to_print=to_print+" "+str(pawn)
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
            dlog(to_print)
    else:
        for i in range(sensor_radius, -sensor_radius-1, -1):
            to_print = ""
            for j in range(sensor_radius, -sensor_radius-1, -1):
                if i == 0 and j == 0:
                    continue
                pawn = check_space_wrapper(game, bot, row+i, col+j, board_size)
                to_print=to_print+" "+str(pawn)
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
            dlog(to_print)

    first_layer.append(dist_to_side(col, board_size))
    first_layer.append(abs(row-backRow))
    if col == 0 or col == board_size-1:
        first_layer.append(1)
    else:
        first_layer.append(0)
    if col == 1 or col == board_size-2:
        first_layer.append(1)
    else:
        first_layer.append(0)

    second_layer = []
    second_layer_len = 20
    test_weights = [[random.randint(0,10) for x in range(len(first_layer))] for y in range(second_layer_len)]
    test_bias = [random.randint(0,10) for x in range(second_layer_len)]

    for i in range(second_layer_len):
        value = test_bias[i]
        for j in range(len(first_layer)):
            value += first_layer[j] * test_weights[i][j]
        second_layer.append(value)
    #dlog('Second layer values: ' + str(second_layer))

    #third layer
    output_layer = []
    output_layer_len = 2
    second_weights = [[random.randint(0,10) for x in range(second_layer_len)] for y in range(output_layer_len)]
    second_bias = [random.randint(0,10) for x in range(output_layer_len)]
    for i in range(output_layer_len):
        tempValue = second_bias[i]
        for j in range(second_layer_len):
            tempValue += second_layer[j] * second_weights[i][j]
        output_layer.append(tempValue)
    #dlog('Output layer values: ' + str(output_layer))
    
    if check_space_wrapper(game, bot, row + forward, col + 1, board_size) == opp_team: # up and right
        game.capture(bot, row + forward, col + 1)

    elif check_space_wrapper(game, bot, row + forward, col - 1, board_size) == opp_team: # up and left
        game.capture(bot, row + forward, col - 1)

    # otherwise try to move forward
    elif row + forward != -1 and row + forward != board_size and not check_space_wrapper(game, bot, row + forward, col, board_size) and output_layer[0] > output_layer[1]:
        #if row < whiteHalfway:
        game.move_forward(bot)


# OVERLORD #

def spawn_weights_pro_plus_max_xyz(board, board_size, bot_num, team, opp_team, backRow):
    weights = []
    for tempCol in range(board_size):
        weights.append(0)

        weight_index = dist_to_side(tempCol, board_size) # different weights depending on how far away from the wall
        if weight_index > 2:
            weight_index = 2 #limit is 2 away

        #check same col
        for tempRow in range(board_size):
            pawn = board[tempRow][tempCol]
            if pawn != None: # there is a pawn
                distance = abs(tempRow-backRow) # distance to pawn from your back row
                if pawn == team: # your pawn
                    weights[tempCol] = weights[tempCol] + sameRowAlliedWeights[weight_index][distance]
                else: # enemy pawn
                    weights[tempCol] = weights[tempCol] + sameRowEnemyWeights[weight_index][distance]

        #check left adjacent col
        if tempCol > 0:
            for tempRow in range(board_size):
                pawn = board[tempRow][tempCol-1]
                if pawn != None: # there is a pawn
                    distance = abs(tempRow-backRow) # distance to pawn from your back row
                    if pawn == team: # your pawn
                        weights[tempCol] = weights[tempCol] + adjacentRowAlliedWeights[weight_index][distance]
                    else: # enemy pawn
                        weights[tempCol] = weights[tempCol] + adjacentRowEnemyWeights[weight_index][distance]

        #check right adjacent col
        if tempCol < board_size-1:
            for tempRow in range(board_size):
                pawn = board[tempRow][tempCol+1]
                if pawn != None: # there is a pawn
                    distance = abs(tempRow-backRow) # distance to pawn from your back row
                    if pawn == team: # your pawn
                        weights[tempCol] = weights[tempCol] + adjacentRowAlliedWeights[weight_index][distance]
                    else: # enemy pawn
                        weights[tempCol] = weights[tempCol] + adjacentRowEnemyWeights[weight_index][distance]
    return weights

def maxIndex(list):
    maxNum = list[0]
    maxIndex = 0
    for i in range(len(list)):
        if list[i] > maxNum:
            maxIndex = i
            maxNum = list[i]
    return maxIndex

def overlord_turn(game,bot,bot_num):
    board_size = game.get_board_size()

    team = game.get_team(bot)

    if team == Team.WHITE:
        backRow = 0
        forward = 1
        opp_team = Team.BLACK
    else:
        backRow = board_size - 1
        forward = -1
        opp_team = Team.WHITE

    board = game.get_board()
    weights = spawn_weights_pro_plus_max_xyz(board, board_size, bot_num, team, opp_team, backRow)
    
    debug = ''
    for i in range(board_size):
        debug = debug + str(weights[i]) + ' '
    dlog(debug)

    for i in range(board_size):
        maxWeightCol = maxIndex(weights)
        if not game.hq_check_space(backRow, maxWeightCol):
            game.spawn(bot, backRow, maxWeightCol)
            break
        else:
            weights[maxWeightCol] = -10000000


# GAME METHODS #

def check_over(game):
    winner = False

    white, black = 0, 0
    for col in range(game.board_size):
        if game.board[0][col] and str(game.board[0][col].team) == "Team.BLACK": black += 1
        if game.board[game.board_size - 1][col] and str(game.board[game.board_size - 1][col].team) == "Team.WHITE": white += 1

    if black >= (game.board_size + 1) // 2:
        winner = True

    if white >= (game.board_size + 1) // 2:
        winner = True

    if game.round > game.max_rounds:
        winner = True

    if winner:
        if white == black:
            tie = True
            for r in range(1, game.board_size):
                if tie:
                    w, b = 0, 0
                    for c in range(game.board_size):
                        if game.board[r][c] and str(game.board[r][c].team) == "Team.BLACK": b += 1
                        if game.board[game.board_size - r - 1][c] and str(game.board[game.board_size - r - 1][c].team) == "Team.WHITE": w += 1
                    if w == b: continue
                    game.winner = "Team.WHITE" if w > b else "Team.BLACK"
                    tie = False
            if tie:
                game.winner = str(random.choice([Team.WHITE, Team.BLACK]))
        else:
            game.winner = "Team.WHITE" if white > black else "Team.BLACK"
        game.running = False

def turn(game,bot_num): #shameless stolen off of the engine ;)
    if game.running:
        game.round += 1

        if game.round > game.max_rounds:
            check_over(game)

        if game.debug:
            game.log_info(f'Turn {game.round}')
            game.log_info(f'Queue: {game.queue}')
            game.log_info(f'Lords: {game.lords}')

        for i in range(game.robot_count):
            if i in game.queue:
                robot = game.queue[i]
                robot.has_moved = False
                pawn_turn(game,robot,bot_num)

                if not robot.runner.initialized:
                    game.delete_robot(i)
                check_over(game)

        if game.running:
            for robot in game.lords:
                robot.has_moved = False
                overlord_turn(game,robot,bot_num)

            game.lords.reverse()  # the HQ's will alternate spawn order
            game.board_states.append([row[:] for row in game.board])
    else:
        raise GameError('game is over')


def test_generation(args): # runs matches between the bots to determine fitness values
    for m in range(matchups_per_bot):
        queue = random.shuffle(list(range(population_size))) #queue to determine matchups

        i = 0
        while i < len(queue):
            random_seed = random.randint(0,1000000)
            #TODO make the game NOT use the code_containers and use 
            game = Game([code_container1, code_container2], board_size=args.board_size, max_rounds=args.max_rounds, 
                    seed=random_seed, debug=False)
            while True:
                if not game.running:
                    break
                turn(game,1)


# GENETIC ALGORITHM #

def calculate_score(game): #Calculate the fitness of each individual bot
    global point_values_list, penalty_values_list
    game_board = game.board
    whiteScore, blackScore = 0,0
    whitePenalty, blackPenalty = 0,0
    for row in range(len(game_board)):
        for col in range(len(game_board[0])):
            if game_board[row][col] and str(game_board[row][col].team) == 'Team.BLACK':
                blackScore += point_values_list[row]
                whitePenalty += penalty_values_list[row]
            elif game_board[row][col] and str(game_board[row][col].team) == 'Team.WHITE':
                whiteScore += point_values_list[len(point_values_list)-1-row]
                blackPenalty += penalty_values_list[len(point_values_list)-1-row]
    return 'White Score: ' + str(whiteScore - whitePenalty) + ', Black Score: ' + str(blackScore-blackPenalty)
    #return game.board

#Cut population by 2/3
def cut_population():
    global example_bots_list
    example_bots_list.sort(key=lambda x: x[1])
    new_generation = []
    #Change example_bots_list to population_size
    for i in range(int(len(example_bots_list)/3)):
        new_generation.append(example_bots_list[len(example_bots_list) - i - 1])
    return new_generation

def generate_random_bot(one_std_overlord_change):
    single_pawn_bias_L1 = ((np.random.rand(hidden_count,input_count)-0.5)*2).tolist()
    single_pawn_weights_L1 = ((np.random.rand(hidden_count,input_count)-0.5)*2).tolist()
    single_pawn_bias_L2 = ((np.random.rand(output_count,hidden_count)-0.5)*2).tolist()
    single_pawn_weights_L2 = ((np.random.rand(output_count,hidden_count)-0.5)*2).tolist()


    single_overlord_weights_same_allied = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(sameRowAlliedWeights)).tolist()
    single_overlord_weights_adjacent_allied = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(adjacentRowAlliedWeights)).tolist()
    single_overlord_weights_same_enemy = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(sameRowEnemyWeights)).tolist()
    single_overlord_weights_adjacent_enemy = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(adjacentRowEnemyWeights)).tolist()

    return single_pawn_bias_L1, single_pawn_weights_L1, single_pawn_bias_L2, single_pawn_weights_L2, single_overlord_weights_same_allied, single_overlord_weights_adjacent_allied, single_overlord_weights_same_enemy, single_overlord_weights_adjacent_enemy

#Create the new generation
def new_generation():
    survivors = cut_population()
    

def train(code_container1,code_container2,args):

    single_pawn_bias_L1, single_pawn_weights_L1, single_pawn_bias_L2, single_pawn_weights_L2, single_overlord_weights_same_allied, single_overlord_weights_adjacent_allied, single_overlord_weights_same_enemy, single_overlord_weights_adjacent_enemy = generate_random_bot(10)

    print(single_pawn_bias_L1)
    print("\n\n\n\n")
    print(single_overlord_weights_same_allied)
    return

    global example_bots_list
    random_seed = random.randint(0,1000000)
    game = Game([code_container1, code_container2], board_size=args.board_size, max_rounds=args.max_rounds, 
            seed=random_seed, debug=False)
    while True:
        if not game.running:
            break
        turn(game,1)

    print(example_bots_list)
    cut_population(game)
    print(example_bots_list)

    print(calculate_score(game))

    print(f'{game.winner} wins!')

if __name__ == '__main__':

    # This is just for parsing the input to the script. Not important.
    parser = argparse.ArgumentParser()
    parser.add_argument('player', nargs='+', help="Path to a folder containing a bot.py file.")
    parser.add_argument('--debug', default='true', choices=('true','false'), help="In debug mode (defaults to true), bot logs and additional information are displayed.")
    parser.add_argument('--max-rounds', default=GameConstants.MAX_ROUNDS, type=int, help="Override the max number of rounds for faster games.")
    parser.add_argument('--board-size', default=GameConstants.BOARD_SIZE, type=int, help="Override the board size for faster games.")
    args = parser.parse_args()
    args.debug = args.debug == 'true'

    # The faulthandler makes certain errors (segfaults) have nicer stacktraces.
    faulthandler.enable() 

    # This is where the interesting things start!

    # Every game needs 2 code containers with each team's bot code.
    code_container1 = CodeContainer.from_directory(args.player[0])
    code_container2 = CodeContainer.from_directory(args.player[1] if len(args.player) > 1 else args.player[0])

    # Here we check if the script is run using the -i flag.
    # If it is not, then we simply play the entire game.

    train(code_container1, code_container2, args)


