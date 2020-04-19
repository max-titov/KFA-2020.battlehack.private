import time
import argparse
import faulthandler
import sys
import threading
import random

from battlehack20 import CodeContainer, Game, BasicViewer, GameConstants




def train(code_container1,code_container2,args):
    
    white_wins = 0
    black_wins = 0
    for game_num in range(args.games):
        random_seed = random.randint(0,1000000)
        game = Game([code_container1, code_container2], board_size=args.board_size, max_rounds=args.max_rounds, 
                seed=random_seed, debug=False)
        while True:
            if not game.running:
                break
            game.turn()

        if str(game.winner) == "Team.WHITE":
            white_wins+=1
        else:
            black_wins+=1
        print(f'{game.winner} wins game {game_num}')

    white_win_rate = float(white_wins)/float(args.games)*100
    print(f'White won {white_wins} games out of {args.games} which is a {white_win_rate}% win rate')

    black_win_rate = float(black_wins)/float(args.games)*100
    print(f'Black won {black_wins} games out of {args.games} which is a {black_win_rate}% win rate')


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


