
class StateManager:
	def __init__(self, root):
		self.root=root
		self.current=""
		self.states={}
	def add_state(self, state, key):
		self.states[key]=state
		self.states[key].bind(self)
	def goto_state(self, key):
		self.states[key].pre_change()
		if self.current!="":
			self.states[self.current].suspend()
		self.current=key
		if not self.states[key]._initilized:
			self.states[key].first_start()
			self.states[key]._initilized=True
		self.states[key].start()
	def run_interdicting(self, key, params):
		return self.states[key].run_once(params)
	def run_tick(self):
		self.states[self.current].update_and_render()

class State:
	def __init__(self):
		self._initilized=False
	def bind(self, statemgr):
		self.state_manager=statemgr
		self.root=statemgr.root
	def pre_change(self):
		pass
	def first_start(self):
		pass
	def start(self):
		pass
	def update_and_render(self):
		pass
	def suspend(self):
		pass

class InterdictingState(State):
	def run_once(self, params):
		pass