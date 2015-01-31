import primitives

class CheckSpeakerFactionPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		return 1

class CheckPlayerFactionPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		return 1

def init_primitives(root, console):
	primitives.register_primitive(root, "SPKRcheckfaction", CheckSpeakerFactionPrimitive)
	primitives.register_primitive(root, "PLYRcheckfaction", CheckPlayerFactionPrimitive)