import primitives, absroot
from logging import debug

class ScanPrimitive(primitives.BasePrimitive):
	def run_in_item(self, item, *a):
		if item.parent.damage.shields<self.config.get("max_shields", 20):
			absroot.state_manager.start_interdicting("inventory", {"ship":item.parent.targeted, "editable":False})

def init_primitives(root, console):
	primitives.register_primitive(root, "scan", ScanPrimitive)