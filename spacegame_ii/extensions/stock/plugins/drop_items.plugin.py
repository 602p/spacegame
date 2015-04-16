import primitives, tasks, particles, absroot, extention_loader
import ship as ship_module
from jsonutil import dget

@extention_loader.add_primitive("drop_inventory")
class DropInventoryOnDeath(primitives.BasePrimitive):
	def run_in_ship(self, ship):
		if (len(ship.inventory)>0 )or 1:
			absroot.state_manager.states["game"].entities.append(
					ship_module.create_ship(self.root, "cargo_pod_generic", ship.rigidbody.x, ship.rigidbody.y, 1,1)
					)
			for item in ship.inventory:
				if item.config.get("is_dropped", True):
					item.reparent(None)
					absroot.state_manager.states["game"].entities[-1].pick_up(item)