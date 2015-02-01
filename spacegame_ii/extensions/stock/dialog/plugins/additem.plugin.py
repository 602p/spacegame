import primitives, item
from logging import debug

class AddItemPrimitive(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		self.root.state_manager.states["game"].player.pick_up(
			item.create_item(self.root, self.config["id"], self.root.state_manager.states["game"].player,
			 self.config.get("equipped", -1),
			 self.config.get("count", None))
		)
		debug("Gave the player "+self.config["id"])

def init_primitives(root, console):
	primitives.register_primitive(root, "player_add_item", AddItemPrimitive)