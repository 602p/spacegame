import primitives
from logging import debug

class LockDialogPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		self.root.dialog_manager.current_state.can_exit=self.config["value"]
		debug("Set CURR_DIALOG_LOCKABILITY to "+str(self.config["value"]))

def init_primitives(root, console):
	primitives.register_primitive(root, "set_current_dialog_exitability", LockDialogPrimitive)