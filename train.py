import time
import argparse
import faulthandler
import sys
import threading
import random
import numpy as np

from battlehack20 import CodeContainer, Game, BasicViewer, GameConstants

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


fitnesses = np.zeros([population_size])

matchups_per_bot = 2

def check_over(self):
    winner = False

    white, black = 0, 0
    for col in range(self.board_size):
        if self.board[0][col] and self.board[0][col].team == Team.BLACK: black += 1
        if self.board[self.board_size - 1][col] and self.board[self.board_size - 1][col].team == Team.WHITE: white += 1

    if black >= (self.board_size + 1) // 2:
        winner = True

    if white >= (self.board_size + 1) // 2:
        winner = True

    if self.round > self.max_rounds:
        winner = True

    if winner:
        if white == black:
            tie = True
            for r in range(1, self.board_size):
                if tie:
                    w, b = 0, 0
                    for c in range(self.board_size):
                        if self.board[r][c] and self.board[r][c].team == Team.BLACK: b += 1
                        if self.board[self.board_size - r - 1][c] and self.board[self.board_size - r - 1][c].team == Team.WHITE: w += 1
                    if w == b: continue
                    self.winner = Team.WHITE if w > b else Team.BLACK
                    tie = False
            if tie:
                self.winner = random.choice([Team.WHITE, Team.BLACK])
        else:
            self.winner = Team.WHITE if white > black else Team.BLACK
        self.running = False

def turn(game): #shameless stolen off of the engine ;)
    if game.running:
        game.round += 1

        if game.round > game.max_rounds:
            game.check_over()

        if game.debug:
            game.log_info(f'Turn {game.round}')
            game.log_info(f'Queue: {game.queue}')
            game.log_info(f'Lords: {game.lords}')

        for i in range(game.robot_count):
            if i in game.queue:
                robot = game.queue[i]
                robot.turn()

                if not robot.runner.initialized:
                    game.delete_robot(i)
                game.check_over()

        if game.running:
            for robot in game.lords:
                robot.turn()

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
                turn(game)


def calculate_score(game):
    global point_values_list
    game_board = game.board
    whiteScore, blackScore = 0,0
    for row in range(len(game_board)):
        for col in range(len(game_board[0])):
            if game_board[row][col] and game_board[row][col].team == Team.BLACK:
                blackScore += point_values_list[row]
            elif game_board[row][col] and game_board[row][col].team == Team.WHITE:
                whiteScore += point_values_list[len(point_values_list)-row]
    #return 'White Score: '+str(whiteScore)+', Black Score: '+str(blackScore)
    return game.board



def train(code_container1,code_container2,args):

    random_seed = random.randint(0,1000000)
    game = Game([code_container1, code_container2], board_size=args.board_size, max_rounds=args.max_rounds, 
            seed=random_seed, debug=True)
    while True:
        if not game.running:
            break
        turn(game)


    print(game.board)

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


