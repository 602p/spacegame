import datetime, absroot
from logging import debug, info, warning, error, critical
import logging
module_logger=logging.getLogger("sg.tasks")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

def init(r):
	r.tasks_index={}
	r.delayed_oo={}

def add_group(root, tag):
	if not tag in root.tasks_index:
		root.tasks_index[tag]=[]
	if not tag in root.delayed_oo:
		root.delayed_oo[tag]=[]

def add_task(root, tag, task):
	debug("adding task "+str(task)+" to "+tag)
	if not tag in root.tasks_index:
		add_group(root, tag)
	root.tasks_index[tag].append(task)

def run_group(root, tag):
	add_group(root, tag)
	for i in root.tasks_index[tag]:
		i.update(root)
		if i.delete:
			del root.tasks_index[tag][root.tasks_index[tag].index(i)]
	for i in root.delayed_oo[tag]:
		i()
	root.delayed_oo[tag]=[]

def delay(function, tag):
	add_group(absroot, tag)
	absroot.delayed_oo[tag].append(function)

class Task:
	def __init__(self, root, update, duration, data=None):
		self._update=update
		self.duration=duration
		self.start=root.game_time
		self.data=data
		self.timeout=duration
		self.delete=False
		self.root=root

	def update(self, root):
		if root.game_time-self.start>self.timeout:
			self.delete=True
		self.curr_time=root.game_time-self.start
		self._update(self, root)