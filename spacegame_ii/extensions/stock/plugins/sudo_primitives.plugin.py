import primitives

class RunWithTargetedAsShip(primitives.BasePrimitive):
	def run_in_item(self, item):
		primitives.do_group_for_ship(self.root, self.config["sudo_primitives"], item.parent.targeted)

class RunWithOwnerAsShip(primitives.BasePrimitive):
	def run_in_item(self, item):
		primitives.do_group_for_ship(self.root, self.config["sudo_primitives"], item.parent)

def init_primitives(root, console):
	primitives.register_primitive(root, "run_with_targeted_as_ship", RunWithTargetedAsShip)
	primitives.register_primitive(root, "run_with_owner_as_ship", RunWithOwnerAsShip)