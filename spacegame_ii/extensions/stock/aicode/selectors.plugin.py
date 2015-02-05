import ai

class LoopRoutine(ai.Routine):
	def __init__(self, routine):
		self.routine=routine

	def act(self, ship):
		self.routine.act(ship)
		self.state=self.routine.get_state()

class SequenceRoutine(ai.Routine):
	def __init__(self, routines):
		self.routines=routines
		self.current=0

	def start(self):
		super(self).start()
		self.routines[self.current].start()

	def act(self, ship):
		self.routines[self.current].act(ship)

		if not self.routines[self.current].done():
			return

		if self.routines[self.current].get_state()=="FAILURE":
			self.log("Routine "+str(self.routines[self.current])+" failed, failing")
			self.fail()
			return

		if self.current==len(self.routines)-1:
			self.state=self.routines[self.current].get_state()
			self.log("Last routine run, finishing")
			return

		self.current+=1
		self.routines[self.current].start()
		self.log("Proceeded to next routine")

class SelectorRoutine(SequenceRoutine):
	def act(self, ship):
		self.routines[self.current].act(ship)

		if not self.routines[self.current].done():
			return

		if self.routines[self.current].get_state()=="SUCCESS":
			self.succeed()

		if self.current==len(self.routines)-1:
			self.state=self.routines[self.current].get_state()
			self.log("Last routine run, finishing")
			return

		self.current+=1
		self.routines[self.current].start()
		self.log("Proceeded to next routine")