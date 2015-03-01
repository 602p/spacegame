import primitives, ai

class SetNPCAIPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		dialog.othership.ai=ai.AIController(dialog.othership, self.config["value"])
	def run_in_ship(self, ship):
		ship.ai=ai.AIController(ship, self.config["value"])

def init_primitives(root, console):
	primitives.register_primitive(root, "set_npc_ai", SetNPCAIPrimitive)