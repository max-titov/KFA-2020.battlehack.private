import time
import argparse
import faulthandler
import sys
import threading
import random
import numpy as np

from battlehack20 import CodeContainer, Game, BasicViewer, GameConstants
from battlehack20.engine.game.team import Team
from battlehack20.engine.game.robottype import RobotType

population_size = 120

input_count = 76
hidden_count = 20
output_count = 2

pawn_bias_L1 = np.zeros([population_size, hidden_count])
pawn_weights_L1 = np.zeros([population_size, input_count, hidden_count])
pawn_bias_L2 = np.zeros([population_size, output_count])
pawn_weights_L2 = np.zeros([population_size, hidden_count, output_count])

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
fitnesses = [[x, 0] for x in range(population_size)]

matchups_per_bot = 2

cut_percentage = 3

dupe_number = 1

random_number = 3

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

DEBUG = 0

def dlog(str):
    if DEBUG > 0:
        print(str)

def check_space_wrapper(game, bot, r, c, board_size):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return False
    try:
        return game.check_space(bot, r, c)
    except:
        return None

def dist_to_side(column, board_size):
    dist1 = column
    dist2 = board_size-1-column
    return dist1 if dist1 < dist2 else dist2

def pawn_turn(game,bot,bot_num):
    board_size = game.get_board_size()

    team = bot.team

    sensor_radius = 2

    if team == Team.WHITE:
        backRow = 0
        forward = 1
        opp_team = Team.BLACK
    else:
        backRow = board_size - 1
        forward = -1
        opp_team = Team.WHITE

    row, col = bot.row,bot.col
    first_layer = np.asarray([])
    count = 0
    if team == Team.WHITE:
        for i in range(-sensor_radius, sensor_radius+1):
            for j in range(-sensor_radius, sensor_radius+1):
                if i == 0 and j == 0:
                    continue
                pawn = check_space_wrapper(game, bot, row+i, col+j, board_size)
                if pawn == team:
                    first_layer[count] = 1
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,0)
                elif pawn == opp_team:
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,1)
                    first_layer = np.append(first_layer,0)
                else:
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,1)
    else:
        for i in range(sensor_radius, -sensor_radius-1, -1):
            for j in range(sensor_radius, -sensor_radius-1, -1):
                if i == 0 and j == 0:
                    continue
                pawn = check_space_wrapper(game, bot, row+i, col+j, board_size)
                if pawn == team:
                    first_layer = np.append(first_layer,1)
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,0)
                elif pawn == opp_team:
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,1)
                    first_layer = np.append(first_layer,0)
                else:
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,0)
                    first_layer = np.append(first_layer,1)

    first_layer = np.append(first_layer,dist_to_side(col, board_size))
    first_layer = np.append(first_layer,abs(row-backRow))
    if col == 0 or col == board_size-1:
        first_layer = np.append(first_layer,1)
    else:
        first_layer = np.append(first_layer,0)
    if col == 1 or col == board_size-2:
        first_layer = np.append(first_layer,1)
    else:
        first_layer = np.append(first_layer,0)

    # second_layer_len = 20
    
    # test_weights = np.asarray([[random.randint(0,10) for x in range(hidden_count)] for y in range(input_count)])
    # test_bias = np.asarray([random.randint(0,10) for x in range(hidden_count)])

    second_layer = np.dot(first_layer,pawn_weights_L1[bot_num,:,:]) + pawn_bias_L1[bot_num,:]

    # for i in range(second_layer_len):
    #     value = test_bias[i]
    #     for j in range(len(first_layer)):
    #         value += first_layer[j] * test_weights[i][j]
    #     second_layer.append(value)
    #dlog('Second layer values: ' + str(second_layer))

    #third layer
    
    # output_layer_len = 2
    # second_weights = np.asarray([[random.randint(0,10) for x in range(output_count)] for y in range(hidden_count)])
    # second_bias = np.asarray([random.randint(0,10) for x in range(output_layer_len)])

    output_layer = np.dot(second_layer,pawn_weights_L2[bot_num,:,:]) + pawn_bias_L2[bot_num,:]
    # for i in range(output_layer_len):
    #     tempValue = second_bias[i]
    #     for j in range(second_layer_len):
    #         tempValue += second_layer[j] * second_weights[i][j]
    #     output_layer.append(tempValue)
    #dlog('Output layer values: ' + str(output_layer))
    
    if check_space_wrapper(game, bot, row + forward, col + 1, board_size) == opp_team: # up and right
        game.capture(row + forward, col + 1)

    elif check_space_wrapper(game, bot, row + forward, col - 1, board_size) == opp_team: # up and left
        game.capture(row + forward, col - 1)

    # otherwise try to move forward
    elif row + forward != -1 and row + forward != board_size and not check_space_wrapper(game, bot, row + forward, col, board_size) and output_layer[0] > output_layer[1]:
        #if row < whiteHalfway:
        game.move_forward()


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

    team = bot.team

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
        if not game.check_space(backRow, maxWeightCol):
            game.new_robot(backRow, maxWeightCol, team, RobotType.PAWN)
            break
        else:
            weights[maxWeightCol] = -10000000


# GAME METHODS #

def check_over(game):
    winner = False

    white, black = 0, 0
    for col in range(game.board_size):
        if game.board[0][col] and game.board[0][col].team == Team.BLACK: black += 1
        if game.board[game.board_size - 1][col] and game.board[game.board_size - 1][col].team == Team.WHITE: white += 1

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
                        if game.board[r][c] and game.board[r][c].team == Team.BLACK: b += 1
                        if game.board[game.board_size - r - 1][c] and game.board[game.board_size - r - 1][c].team == Team.WHITE: w += 1
                    if w == b: continue
                    game.winner = Team.WHITE if w > b else Team.BLACK
                    tie = False
            if tie:
                game.winner = random.choice([Team.WHITE, Team.BLACK])
        else:
            game.winner = Team.WHITE if white > black else Team.BLACK
        game.running = False

# def turn(game,bot_num): #shameless stolen off of the engine ;)
#     if game.running:
#         game.round += 1

#         if game.round > game.max_rounds:
#             check_over(game)

#         if game.debug:
#             game.log_info(f'Turn {game.round}')
#             game.log_info(f'Queue: {game.queue}')
#             game.log_info(f'Lords: {game.lords}')
#         for i in range(game.robot_count):
#             if i in game.queue:
#                 robot = game.queue[i]
#                 robot.has_moved = False
#                 if robot.type == RobotType.PAWN:
#                     pawn_turn(game,robot,bot_num)

#                 check_over(game)

#         if game.running:
#             for robot in game.lords:
#                 robot.has_moved = False
#                 overlord_turn(game,robot,bot_num)

#             game.lords.reverse()  # the HQ's will alternate spawn order
#             game.board_states.append([row[:] for row in game.board])
#         print(game.board)
#     else:
#         raise GameError('game is over')

def turn(game, bot_index_white, bot_index_black):
    game.round += 1

    if game.round > game.max_rounds:
        check_over(game)

    #print(game.round)

    for i in range(game.robot_count):
        if i in game.queue:
            game.robot = game.queue[i]
            bot_index = 0
            if game.robot.team == Team.WHITE:
                bot_index = bot_index_white
            else:
                bot_index = bot_index_black
            if game.robot.type == RobotType.PAWN:
                pawn_turn(game,game.robot,bot_index)
            else:
                overlord_turn(game,game.robot,bot_index)

            check_over(game)


    if game.running:
        game.queue[0], game.queue[1] = game.queue[1], game.queue[0] # Alternate spawn order of Overlords

<<<<<<< HEAD
=======
# WRITING TO FILE SYSTEM #

def dir_name_generator(num):
    dirLen = 4
    newDir = ""
    while len(newDir)+len(str(num)) < dirLen:
        newDir=newDir+"0"
    return newDir+str(num)

def save_weights(best_bot):
    newDir = dir_name_generator(generation)
    
    os.mkdir(weights_dir+newDir)
    
    # all weights
    f=open(weights_dir+newDir+"/all_weights.txt", "w")

    #pawn weights
    for i in range(len(pawn_bias_L1)):
        for j in range(len(pawn_bias_L1[0])):
            f.write("%f\n"%pawn_bias_L1[i][j])

    for i in range(len(pawn_weights_L1)):
        for j in range(len(pawn_weights_L1[0])):
            for k in range(len(pawn_weights_L1[0][0])):
                f.write("%f\n"%pawn_weights_L1[i][j][k])

    for i in range(len(pawn_bias_L2)):
        for j in range(len(pawn_bias_L2[0])):
            f.write("%f\n"%pawn_bias_L2[i][j])

    for i in range(len(pawn_weights_L2)):
        for j in range(len(pawn_weights_L2[0])):
            for k in range(len(pawn_weights_L2[0][0])):
                f.write("%f\n"%pawn_weights_L2[i][j][k])

    #overlord weights
    for i in range(len(overlord_weights_same_allied)):
        for j in range(len(overlord_weights_same_allied[0])):
            for k in range(len(overlord_weights_same_allied[0][0])):
                f.write("%f\n"%overlord_weights_same_allied[i][j][k])

    for i in range(len(overlord_weights_adjacent_allied)):
        for j in range(len(overlord_weights_adjacent_allied[0])):
            for k in range(len(overlord_weights_adjacent_allied[0][0])):
                f.write("%f\n"%overlord_weights_adjacent_allied[i][j][k])

    for i in range(len(overlord_weights_same_enemy)):
        for j in range(len(overlord_weights_same_enemy[0])):
            for k in range(len(overlord_weights_same_enemy[0][0])):
                f.write("%f\n"%overlord_weights_same_enemy[i][j][k])

    for i in range(len(overlord_weights_adjacent_enemy)):
        for j in range(len(overlord_weights_adjacent_enemy[0])):
            for k in range(len(overlord_weights_adjacent_enemy[0][0])):
                f.write("%f\n"%overlord_weights_adjacent_enemy[i][j][k])

    f.close() 

    #best bot weights

    f=open(weights_dir+newDir+"/best_bot.txt", "w")

    #pawn weights
    for j in range(len(pawn_bias_L1[0])):
        f.write("%f\n"%pawn_bias_L1[best_bot][j])

    for j in range(len(pawn_weights_L1[0])):
        for k in range(len(pawn_weights_L1[0][0])):
            f.write("%f\n"%pawn_weights_L1[best_bot][j][k])

    for j in range(len(pawn_bias_L2[0])):
        f.write("%f\n"%pawn_bias_L2[best_bot][j])

    for j in range(len(pawn_weights_L2[0])):
        for k in range(len(pawn_weights_L2[0][0])):
            f.write("%f\n"%pawn_weights_L2[best_bot][j][k])

    #overlord weights
    for j in range(len(overlord_weights_same_allied[0])):
        for k in range(len(overlord_weights_same_allied[0][0])):
            f.write("%f\n"%overlord_weights_same_allied[best_bot][j][k])

    for j in range(len(overlord_weights_adjacent_allied[0])):
        for k in range(len(overlord_weights_adjacent_allied[0][0])):
            f.write("%f\n"%overlord_weights_adjacent_allied[best_bot][j][k])

    for j in range(len(overlord_weights_same_enemy[0])):
        for k in range(len(overlord_weights_same_enemy[0][0])):
            f.write("%f\n"%overlord_weights_same_enemy[best_bot][j][k])

    for j in range(len(overlord_weights_adjacent_enemy[0])):
        for k in range(len(overlord_weights_adjacent_enemy[0][0])):
            f.write("%f\n"%overlord_weights_adjacent_enemy[best_bot][j][k])

                    




# GENETIC ALGORITHM #
>>>>>>> 6d65b46ce225f8ee0c0a7bf8e6070175edc07da4

def test_generation(code_container1, args): # runs matches between the bots to determine fitness values
    for m in range(matchups_per_bot):
        queue = list(range(population_size)) #queue to determine matchups
        random.shuffle(queue)

        i = 0
        while i < len(queue):
            bot1 = queue[i]
            bot2 = queue[i+1]
            print("playing "+str(bot1)+" against "+ str(bot2))
            random_seed = random.randint(0,1000000)
            #TODO make the game NOT use the code_containers and use 
            game = Game([code_container1, code_container1], board_size=args.board_size, max_rounds=args.max_rounds, 
                    seed=random_seed, debug=False)
            while True:
                if not game.running:
                    break
                turn(game,queue[bot1],queue[bot2])
            
            whiteScore,blackScore=calculate_score(game)

            fitnesses[bot1][1] = fitnesses[bot1][1] + whiteScore
            fitnesses[bot2][1] = fitnesses[bot2][1] + blackScore

            i+=2
    print(fitnesses)


# GENETIC ALGORITHM #

def calculate_score(game): #Calculate the fitness of each individual bot
    global point_values_list, penalty_values_list
    game_board = game.board
    whiteScore, blackScore = 0,0
    whitePenalty, blackPenalty = 0,0
    for row in range(len(game_board)):
        for col in range(len(game_board[0])):
            if game_board[row][col] and game_board[row][col].team == Team.BLACK:
                blackScore += point_values_list[row]
                whitePenalty += penalty_values_list[row]
            elif game_board[row][col] and game_board[row][col].team == Team.WHITE:
                whiteScore += point_values_list[len(point_values_list)-1-row]
                blackPenalty += penalty_values_list[len(point_values_list)-1-row]
    whiteScore=whiteScore-whitePenalty
    blackScore=blackScore-blackPenalty
    return whiteScore,blackScore
    #return game.board

#Cut population by 2/3 also change from example_bots_list to the real bots list
def cut_population():
    global fitnesses, cut_percentage
    fitnesses.sort(key=lambda x: x[1])
    new_generation = []
    #Change example_bots_list to population_size
    for i in range(int(len(fitnesses)/cut_percentage)):
        new_generation.append(fitnesses[len(fitnesses) - i - 1])
    return new_generation

def generate_random_bot(one_std_overlord_change):
    single_pawn_bias_L1 = ((np.random.rand(hidden_count)-0.5)*2).tolist()
    single_pawn_weights_L1 = ((np.random.rand(input_count,hidden_count)-0.5)*2).tolist()
    single_pawn_bias_L2 = ((np.random.rand(output_count)-0.5)*2).tolist()
    single_pawn_weights_L2 = ((np.random.rand(hidden_count,output_count)-0.5)*2).tolist()
<<<<<<< HEAD
    single_overlord_weights_same_allied = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(sameRowAlliedWeights)).tolist()
    single_overlord_weights_adjacent_allied = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(adjacentRowAlliedWeights)).tolist()
    single_overlord_weights_same_enemy = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(sameRowEnemyWeights)).tolist()
    single_overlord_weights_adjacent_enemy = (np.random.standard_normal(size=(weight_zones,board_size))*one_std_overlord_change+np.asarray(adjacentRowEnemyWeights)).tolist()
=======

    single_overlord_weights_same_allied = (np.random.rand(weight_zones,board_size)*one_std_overlord_change+np.asarray(sameRowAlliedWeights)).tolist()
    single_overlord_weights_adjacent_allied = (np.random.rand(weight_zones,board_size)*one_std_overlord_change+np.asarray(adjacentRowAlliedWeights)).tolist()
    single_overlord_weights_same_enemy = (np.random.rand(weight_zones,board_size)*one_std_overlord_change+np.asarray(sameRowEnemyWeights)).tolist()
    single_overlord_weights_adjacent_enemy = (np.random.rand(weight_zones,board_size)*one_std_overlord_change+np.asarray(adjacentRowEnemyWeights)).tolist()
>>>>>>> 24c87183d24774f355ae8e8d0d2bab4b4ba389dc

    return single_pawn_bias_L1, single_pawn_weights_L1, single_pawn_bias_L2, single_pawn_weights_L2, single_overlord_weights_same_allied, single_overlord_weights_adjacent_allied, single_overlord_weights_same_enemy, single_overlord_weights_adjacent_enemy

#Create the new generation
def new_generation():
    global population_size, cut_percentage, dupe_number, random_number
    survivors = cut_population()
    
    #Pawn stuff
    new_layer1_bias = pawn_bias_L1
    new_layer1_weights = pawn_weights_L1
    new_layer2_bias = pawn_bias_L2
    new_layer2_weights = pawn_weights_L2
    #Overlord stuff
    new_same_allied = overlord_weights_same_allied
    new_adjacent_allied = overlord_weights_adjacent_allied
    new_same_enemy = overlord_weights_same_enemy
    new_adjacent_enemy = overlord_weights_adjacent_enemy

    #print("NSA len: "+str(len(new_same_allied)))
    #print("NSA[0] len: "+str(len(new_same_allied[0])))
    #print("NSA[0][0] len: "+str(len(new_same_allied[0][0])))
    #print("NSA[0][0][0]: "+str(new_same_allied[0][0][0]))

    #reading in and duplicating survivors
    for j in range(population_size//dupe_number):
        for i in range(len(survivors)):
            #print("Survivor original index: "+str((survivors[i])[0]))
            #print("Survivor pawn bias: "+str(pawn_bias_L1[(survivors[i])[0]]))
            new_layer1_bias[i] = pawn_bias_L1[(survivors[i])[0]]
            #for j in range(len(new_layer1_weights[0])):    
            new_layer1_weights[i] = pawn_weights_L1[(survivors[i])[0]]    
            new_layer2_bias[i] = pawn_bias_L2[(survivors[i])[0]]
            #for j in range(len(new_layer2_weights)):    
            new_layer2_weights[i] = pawn_weights_L2[(survivors[i])[0]]
            #for j in range(len(new_same_allied)):
            new_same_allied[i] = overlord_weights_same_allied[(survivors[i])[0]]
            #for j in range(len(new_adjacent_allied)):
            new_adjacent_allied[i] = overlord_weights_adjacent_allied[(survivors[i])[0]]
            #for j in range(len(new_same_enemy)):
            new_same_enemy[i] = overlord_weights_same_enemy[(survivors[i])[0]]
            #for j in range(len(new_adjacent_enemy)):
            new_adjacent_enemy[i] = overlord_weights_adjacent_enemy[(survivors[i])[0]]

    #creating and reading in randomly generated bots
    for i in range(population_size//random_number):
        s_l1_bias, s_l1_weight, s_l2_bias, s_l2_weight, s_same_a, s_adjacent_a, s_same_e, s_adjacent_e = generate_random_bot(10)
        new_layer1_bias[i] = s_l1_bias
        new_layer2_bias[i] = s_l2_bias
        #for j in range(len(s_l1_weight)):
        new_layer1_weights[i] = s_l1_weight
        #for j in range(len(s_l2_weight)):
        new_layer2_weights[i] = s_l2_weight
        #for j in range(len(s_same_a)):
        new_same_allied[i] = s_same_a
        #for j in range(len(s_adjacent_a)):
        new_adjacent_allied[i] = s_adjacent_a
        #for j in range(len(s_same_e)):
        new_same_enemy[i] = s_same_e
        #for j in range(len(s_adjacent_e)):
        new_adjacent_enemy[i] = s_adjacent_e

        #print("New layer1 weights: "+str(new_layer1_weights[0]))
    print("NSA len: "+str(len(new_same_allied)))
    print("NSA[0] len: "+str(len(new_same_allied[0])))
    print("NSA[0][0] len: "+str(len(new_same_allied[0][0])))
    print("NSA[0][0][0]: "+str(new_same_allied[0][0][0]))
    #5% chance of a mutation within each item field --> changes are between -25% and 25%
    print("OWSA len: " + str(len(overlord_weights_same_allied)))
    print("OWSA[0] len: "+str(len(overlord_weights_adjacent_allied[0])))
    print("OWSA[0][0] len: "+str(len(overlord_weights_adjacent_allied[0][0])))
    print("overlord_weights_same_allied[0][0]: "+str(len(overlord_weights_same_allied[0][0])))
    for i in range(population_size):
        for j in range(len(pawn_bias_L1[0])):
            randFloat = random.uniform(0,1)
            if randFloat < 0.05:
                new_layer1_bias[i][j] += random.uniform(-0.25, 0.25)*new_layer1_bias[i][j]
            elif randFloat > 0.99: 
                new_layer1_bias[i][j] = random.uniform(-10,10)
        print('success 1')
        for j in range(len(pawn_weights_L1[0])):
            for z in range(len(pawn_weights_L1[0][0])):
                randFloat = random.uniform(0,1)
                if randFloat < 0.05: 
                    new_layer1_weights[i][j][z] += random.uniform(-0.25, 0.25)*new_layer1_weights[i][j][z]
                elif randFloat > 0.99:
                    new_layer1_weights[i][j][z] = random.uniform(-10,10)
        print('success 2')
        for j in range(len(pawn_bias_L2[0])):
            randFloat = random.uniform(0,1)
            if randFloat < 0.05: 
                new_layer2_bias[i][j] += random.uniform(-0.25, 0.25)*new_layer2_bias[i][j]
            elif randFloat > 0.99:
                new_layer2_bias[i][j] = random.uniform(-10,10)
        print('success 3')
        for j in range(len(pawn_weights_L2[0])):
            for z in range(len(pawn_weights_L2[0][0])):
                randFloat = random.uniform(0,1)
                if randFloat < 0.05: 
                    new_layer2_weights[i][j][z] += random.uniform(-0.25, 0.25)*new_layer2_weights[i][j][z]
                elif randFloat > 0.99:
                    new_layer2_weights[i][j][z] = random.uniform(-10,10)
        print('success 4')
        for j in range(len(overlord_weights_same_allied[0])):
            for z in range(len(overlord_weights_same_allied[0][0])):
                randFloat = random.uniform(0,1)
                if randFloat < 0.05: 
                    new_same_allied[i][j][z] += random.uniform(-0.25, 0.25)*new_same_allied[i][j][z]
                elif randFloat > 0.99:
                    new_same_allied[i] = random.uniform(-10,10)
        print('success 5')
        for j in range(len(overlord_weights_adjacent_allied[0])):
            for z in range(len(overlord_weights_adjacent_allied[0][0])):
                randFloat = random.uniform(0,1)
                if randFloat < 0.05: 
                    new_adjacent_allied[i][j][z] += random.uniform(-0.25, 0.25)*new_adjacent_allied[i][j][z]
                elif randFloat > 0.99:
                    new_adjacent_allied[i] = random.uniform(-10,10)
        print('success 6')
        for j in range(len(overlord_weights_same_enemy[0])):
            for z in range(len(overlord_weights_same_enemy[0][0])):
                randFloat = random.uniform(0,1)
                if randFloat < 0.05: 
                    new_same_enemy[i][j][z] += random.uniform(-0.25, 0.25)*new_same_enemy[i][j][z]
                elif randFloat > 0.99:
                    new_same_enemy[i] = random.uniform(-10,10)
        print('success 7')
        for j in range(len(overlord_weights_adjacent_enemy[0])):
            for z in range(len(overlord_weights_adjacent_enemy[0][0])):
                randFloat = random.uniform(0,1)
                if randFloat < 0.05: 
                    new_adjacent_enemy[i][j][z] += random.uniform(-0.25, 0.25)*new_adjacent_enemy[i][j][z]
                elif randFloat > 0.99:
                    new_adjacent_enemy[i] = random.uniform(-10,10)
        print('success 8')

    #reset fitnesses
    fitnesses = [[x, 0] for x in range(population_size)]

def train(code_container1,args):

<<<<<<< HEAD
    #test_generation(code_container1, args)
    #return;
=======

    # save_weights(1)
    # #test_generation(code_container1, args)
    # return;

>>>>>>> 24c87183d24774f355ae8e8d0d2bab4b4ba389dc

    global example_bots_list
    random_seed = random.randint(0,1000000)
    robot_count = 0
    game = Game([code_container1, code_container1], board_size=args.board_size, max_rounds=args.max_rounds, 
            seed=random_seed, debug=False)
    while True:
        if not game.running:
            break
        turn(game,1,1)

    new_generation()
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

    train(code_container1, args)


