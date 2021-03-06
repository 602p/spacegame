from logging import debug, info, warning, error
from jsonutil import dget
import traceback, sys
import logging
module_logger=logging.getLogger("sg.ai")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	root.ai_hint_keys={}
	root.ai_update_keys={}

def add_hint_node(root, key, func):
	root.ai_hint_keys[key]=func

def get_ai_hint(root, key):
	return root.ai_hint_keys[key]

def has_ai_hint(root, key):
	return key in root.ai_hint_keys.keys()

def add_update_node(root, key, func):
	root.ai_update_keys[key]=func

def get_ai_update(root, key):
	return root.ai_update_keys[key]

def has_ai_update(root, key):
	return key in root.ai_update_keys.keys()

class AIController(object):
	"""
	Manages all controller nodes for the ship
	"""
	def __init__(self, ship, config):
		self.enabled=True
		self.ship=ship
		self.root=ship.root
		self.entities=ship.root.state_manager.states["game"].entities
		self.gamestate=ship.root.state_manager.states["game"]
		self.controllers=[]
		self.can_fire=1
		self.database={}

		for subcontroller in config["ai_subcontrollers"]: #Get all the subcontrollers from the ai defintion...
			if has_ai_update(self.root, subcontroller["controller"]):
				self.controllers.append(get_ai_update(self.root, subcontroller["controller"])(self, subcontroller)) #And instanciate them

	def update(self):
		try:
			for controller in self.controllers:
				controller.update()

			if self.can_fire:
				i=0
				priorities={}
				while i!=len(self.ship.hardpoints): #for each item equipped
					if self.ship.get_item_in_hardpoint(i):
						fire=True
						for hint in self.ship.get_item_in_hardpoint(i).ai_hints:
							if not hint.get_suggested(self): #check if any of the AIItemHints disagree
								fire = False
							
						if fire:
							priorities[i]=dget(self.ship.get_item_in_hardpoint(i)._config, "ai_priority", 5)
					i+=1
				if self.ship.targeted:
					for i in sorted(priorities, key=lambda hardpoint: priorities[hardpoint]):
						self.ship.get_item_in_hardpoint(i).fire() #then fire
		except BaseException as e:
			if not (isinstance(e, AttributeError) and "_config" not in str(e)):
				error("AI ERROR (BASE): " + str(e))
				exc_type, exc_value, exc_traceback = sys.exc_info()
				for i in traceback.format_exception(exc_type, exc_value, exc_traceback): error(i)
				

	def enable(self):
		self.enabled=True
	def disable(self):
		self.enabled=False

	def save_to_config_node(self):
		controllers=[]
		for controller in self.controllers:
			controllers.append(controller.save_to_config_node())
		return {
			"controllers":controllers,
			"database":self.database
		}

class AIItemHint:
	def __init__(self, item, config):
		self.config=config
		self.item=item
	def get_suggested(self, ai):
		pass

class AIControllerUpdateNode:
	def __init__(self, ai_controller, config):
		self.controller=ai_controller
		self.config=config
		self.ship=ai_controller.ship
		self.database={}
		self.init()
	def init(self):
		pass
	def update(self):
		pass
	def save_to_config_node(self):
		return {
			"config":self.config,
			"database":self.database
		}

def _load_node(root, config, controller):
	#print config
	controller.controllers.append(
		get_ai_update(root, config["config"]["controller"])(controller, config["config"])
		)
	controller.controllers[-1].database=config["database"]

def _load_controller(root, ship, config):
	#print config
	cont=AIController(ship, {"ai_subcontrollers":[]})
	for node in config["controllers"]:
		_load_node(root, node, cont)
	cont.database=config["database"]
	return cont