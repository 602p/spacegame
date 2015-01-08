
class StateManager:
	def __init__(self, root):
		self.root=root
		self.current=""
		self.states={}
	def add_state(self, state, key):
		self.states[key]=state
		self.states[key].bind(self)
	def goto_state(self, key, params=123):
		self.states[key].pre_change()
		if self.current!="":
			self.states[self.current].suspend()
		self.current=key
		if not self.states[key]._initilized:
			self.states[key].first_start()
			self.states[key]._initilized=True
		self.states[key].set_params(params)
		self.states[key].start()
	def start_interdicting(self, state, params, callback=lambda s, a:0, callback_args=None):
		def packed_callback(self):
			callback(self, callback_args)
		self.states[state].callback=packed_callback
		self.goto_state(state, params)
	def run_tick(self):
		self.states[self.current].update_and_render()
	def process_events(self, events):
		self.states[self.current].process_events(events)

class State:
	def __init__(self):
		self._initilized=False
	def bind(self, statemgr):
		self.state_manager=statemgr
		self.root=statemgr.root
		self.params=None
		self._init()
	def _init(self):
		pass
	def set_params(self, params):
		self.params=params
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
	def get_return(self):
		return -1
	def process_events(self, events):
		pass

class InterdictingState(State):
	def pre_change(self):
		self.last=self.state_manager.current
		self.last_params=self.state_manager.states[self.state_manager.current].params
		self.done=False
		self.return_value=-1

	def finish(self, value=-1):
		self.done=True
		self.return_value=value

	def get_return(self):
		return self.return_value

	def update_and_render(self):
		if not self.done:
			self.internal_update()
		else:
			self.state_manager.goto_state(self.last, self.last_params)

	def internal_update(self):
		pass

