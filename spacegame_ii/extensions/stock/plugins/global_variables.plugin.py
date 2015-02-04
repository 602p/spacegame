import primitives
from logging import debug

class CheckVariablePrimitive(primitives.BasePrimitive):
	def check(self):
		v=self.root.savegame.database.get(self.config["name"], self.config.get("default", None))==self.config["value"]
		#debug("Checking var "+self.config["name"]+" :: "+str(v))
		return v
	def run_in_dialog(self, dialog, speech):
		r=self.check()
		if r:
			primitives.do_group_for_dialog(self.root, self.config.get("effects",[]), dialog, speech)
		else:
			primitives.do_group_for_dialog(self.root, self.config.get("else",[]), dialog, speech)
		return r

	def run_in_event(self, event):
		r=self.check()
		if r:
			primitives.do_group_for_event(self.root, self.config.get("effects",[]), event)
		else:
			primitives.do_group_for_event(self.root, self.config.get("else",[]), event)
		return r

class SetVariablePrimitive(primitives.BasePrimitive):
	def do(self):
		self.root.savegame.database[self.config["name"]]=self.config["value"]
	def run_in_dialog(self, *a, **k):
		self.do()
	def run_in_event(self, *a, **k):
		self.do()

def init_primitives(root, console):
	primitives.register_primitive(root, "check_variable", CheckVariablePrimitive)
	primitives.register_primitive(root, "set_variable", SetVariablePrimitive)