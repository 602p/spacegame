import primitives, ship, random
from logging import debug, info, warn, error, critical

class SpawnShipPrimitive(primitives.BasePrimitive):
	def run_in_event(self, event):
		if self.config["pos"]=="random":
			pos_x=self.root.state_manager.states["game"].player.rigidbody.x+random.uniform(-self.config["random_within_x"][0],self.config["random_within_x"][1])
			pos_y=self.root.state_manager.states["game"].player.rigidbody.y+random.uniform(-self.config["random_within_y"][0],self.config["random_within_y"][1])

		entity=ship.create_ship(
				self.root,
				self.config["ship_id"],
				pos_x,
				pos_y
			)

		self.root.state_manager.states["game"].entities.append(entity)

		if "internal_id" in self.config:
			event.database["ship_mappings"][self.config["internal_id"]]=entity.hash_id

		if "add_triggers" in self.config:
			for group in self.config["add_triggers"]:
				entity.add_trigger(group["group"], group["primitive"])

def init_primitives(root,console):
	primitives.register_primitive(root, "spawn_ship", SpawnShipPrimitive)