import primitives, item
from logging import debug

class AddItemPrimitive(primitives.BasePrimitive):
	def run_in_default(self, *a, **k):
		for key in k:
			exec key+"=k[key]"
		pcount=self.config.get("count", None)
		if pcount is not None:
			if isinstance(pcount, basestring):
				if pcount.startswith("*"):
					pcount=eval(pcount[1:])
		self.root.state_manager.states["game"].player.pick_up(
			item.create_item(self.root, self.config["id"], self.root.state_manager.states["game"].player,
			 self.config.get("equipped", -1),
			 pcount)
		)
		debug("Gave the player "+self.config["id"])

	def run_in_event(self, event):
		self.run_in_default(event=event)

def init_primitives(root, console):
	primitives.register_primitive(root, "player_add_item", AddItemPrimitive)