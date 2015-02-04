import primitives, ship, random
from logging import debug, info, warn, error, critical
import entitybase as eb

class FinishQuest(primitives.BasePrimitive):
	def run_in_ship(self, ship):
		self.root.quest_manager.get_quest_for_ship(ship.hash_id).finish()
	def run_in_trigger(self, *a, **k):
		self.root.quest_manager.get_quest_for_ship(k["ship"].hash_id).finish()

def init_primitives(root,console):
	primitives.register_primitive(root, "finish_event", FinishQuest)
	primitives.register_primitive(root, "finish_quest", FinishQuest)