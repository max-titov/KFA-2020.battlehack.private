class Overlord:

	def turn():
		dlog('Starting Turn!')
	    board_size = get_board_size()

	    team = get_team()
	    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
	    dlog('Team: ' + str(team))

	    robottype = get_type()
	    dlog('Type: ' + str(robottype))

	    if team == Team.WHITE:
            index = 0
        else:
            index = board_size - 1

        for _ in range(board_size):
            i = random.randint(0, board_size - 1)
            if not check_space(index, i):
                spawn(index, i)
                dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
                break