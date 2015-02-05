import ai

class MoveTo(ai.Routine):
	def __init__(self, dx, dy):
		self.destx=dx
		self.desty=dy

	def act(self, ship):
		pass