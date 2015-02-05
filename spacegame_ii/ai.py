from logging import debug, info, warning, error
from jsonutil import dget
import traceback, sys

def init(root):
	pass

class Routine(object):
	def start(self):
		self.state="RUNNING"
		self.log("Starting...")

	def end(self):
		self.log("Finished")

	def act(self, ship):
		pass

	def succeed(self):
		self.state="SUCCESS"
		self.log("Success!")
		self.end()

	def fail(self):
		self.state="FAILURE"
		self.log("Failed!")
		self.end()

	def done(self):
		return self.get_state()!="RUNNING"

	def get_state(self):
		return self.state

	def log(self, t):
		debug("["+self.__class__.__name__+"]:"+t)