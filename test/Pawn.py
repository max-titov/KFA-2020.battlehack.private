import Robot
class Pawn(Robot):

	def init(self, white):
		Robot.init(self, white)

	def turn(self):
		row, col = get_location()
		dlog('My location is: ' + str(row) + ' ' + str(col))

		if self.white:
			forward = 1
		else:
			forward = -1

		# try catpuring pieces
		if check_space_wrapper(row + forward, col + 1, self.board_size) == self.opp_team: # up and right
			capture(row + forward, col + 1)
			dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

		elif check_space_wrapper(row + forward, col - 1, self.board_size) == self.opp_team: # up and left
			capture(row + forward, col - 1)
			dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

		# otherwise try to move forward
		elif row + forward != -1 and row + forward != self.board_size and not check_space_wrapper(row + forward, col, self.board_size):
			#               ^  not off the board    ^            and    ^ directly forward is empty
			move_forward()
			dlog('Moved forward!')

		confusion = "you need a line here to avoid segfault. we aren't sure why but are working on it"
		# ^ I think this is related to the potential ambiguity of what the following else is referring to?