import primitives

class CheckSpeakerShipPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		return self.config["ship"]==dialog.othership.id_string

class CheckPlayerShipPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		return self.config["ship"]==self.root.state_manager.states["game"].player.id_string

def init_primitives(root, console):
	primitives.register_primitive(root, "SPKRcheckship", CheckSpeakerShipPrimitive)
	primitives.register_primitive(root, "PLYRcheckship", CheckPlayerShipPrimitive)