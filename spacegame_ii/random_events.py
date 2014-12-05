import random
from jsonutil import dget

class RandomEvent:
	def __init__(self, config):
		self.id=config["id"]
		self.name=dget(config, "name", "EVENT NAME")
		self.can_be_random=dget(config, "spawn_random", True)