import primitives
from logging import debug

class CheckRelationsPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		debug("Checking relations...")
		if "above" in self.config:
			return dialog.othership.player_relations>self.config["above"]
		if "below" in self.config:
			return dialog.othership.player_relations<self.config["below"]

class ModRelationsPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		debug("Checking relations...")
		dialog.othership.player_relations+=self.config["amount"]

def init_primitives(root, console):
	primitives.register_primitive(root, "check_reputation", CheckRelationsPrimitive)
	primitives.register_primitive(root, "mod_reputation", ModRelationsPrimitive)