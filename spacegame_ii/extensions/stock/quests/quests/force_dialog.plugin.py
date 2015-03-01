import primitives, ship, random
from logging import debug, info, warn, error, critical
import entitybase as eb

class ForceHailPrimitive(primitives.BasePrimitive):
	def run_in_event(self, event):
		self.root.dialog_manager.start_dialog(eb.get_entity_by_hid(self.root, event.database["ship_mappings"][self.config["ship"]]), self.config.get("topic", "greeting"))
	def run_in_trigger(self, context=None, **k):
		#print "SSS"
		self.root.dialog_manager.start_dialog(context, self.config.get("topic", "greeting"))

def init_primitives(root,console):
	primitives.register_primitive(root, "force_hail", ForceHailPrimitive)