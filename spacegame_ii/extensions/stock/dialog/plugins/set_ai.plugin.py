import primitives, ai

class SetNPCAIPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		dialog.othership.ai=ai.AIController(dialog.othership, self.config["value"])
		dialog.othership.targeted=None
	def run_in_trigger(self, context=None, **k):
		print "_SSS"
		context.ai=ai.AIController(context, self.config["value"])
		context.targeted=None

def init_primitives(root, console):
	primitives.register_primitive(root, "set_npc_ai", SetNPCAIPrimitive)