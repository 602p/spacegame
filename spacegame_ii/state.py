import random, datetime
from logging import debug, info, warning, error, critical

class StateManager:
	def __init__(self, root):
		self.root=root
		self.current=""
		self.states={}
		self.factories={}
	def add_state(self, state, key):
		self.states[key]=state
		self.states[key].bind(self)
	def goto_state(self, key, params=123):
		self.states[key].pre_change()
		if self.current!="":
			self.states[self.current].suspend()
		self.current=key
		self.states[key].set_params(params)
		if not self.states[key]._initilized:
			self.states[key].first_start()
			self.states[key]._initilized=True
		self.states[key].start()
	def start_interdicting(self, state, params):
		_temp_state=state+"_built"+str(datetime.datetime.now().time().isoformat())
		self.add_state(self.factories[state](), _temp_state)
		debug("Temporary state created as "+_temp_state)
		self.goto_state(_temp_state, params)
		return self.states[_temp_state]
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
		if not 'last' in dir(self):
			debug("starting interdicting state...")
			self.last=self.state_manager.current
			debug("captured last state as "+self.last)
			self.last_params=self.state_manager.states[self.state_manager.current].params
			self.done=False
			self.return_value=-1
		else:
			debug("old state already captured.")

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

class InterdictingStateFactory:
	def __init__(self, type_):
		self.type_=type_

	def __call__(self):
		debug("[InterdictingStateFactory] Instanciating a "+str(self.type_))
		return self.type_()