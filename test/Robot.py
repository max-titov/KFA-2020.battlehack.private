class Robot:

	def __init__(self, white):
		self.white = white
		self.board_size = get_board_size()
		team = get_team()
	    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
