import Robot
class Overlord(Robot):

	def init(self, white):
		Robot.init(self, white)

	def turn(self):

		if self.white:
			index = 0 
		else: 
			index = self.board_size - 1

		for _ in range(self.board_size):
			i = random.randint(0, self.board_size - 1)
			if not check_space(index, i):
				spawn(index, i)
				dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
				break