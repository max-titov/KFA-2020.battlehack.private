class Robot:

	def init(self, white):
		self.white = white
		self.board_size = get_board_size()
		self.team = get_team()
		self.opp_team = Team.WHITE if team == Team.BLACK else team.BLACK