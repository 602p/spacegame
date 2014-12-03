import ai
from rotutil import get_angle, get_rel_angle
from jsonutil import dget

class SelectPlayer(ai.AIControllerUpdateNode):
	def update(self):
		self.controller.ship.targeted=self.controller.gamestate.player

class PointAtSelected(ai.AIControllerUpdateNode):
	def update(self):
		delta_angle=get_rel_angle(get_angle(self.ship.rotated_rect.center[0], self.ship.targeted.rotated_rect.center[0],
			self.ship.rotated_rect.center[1], self.ship.targeted.rotated_rect.center[1]), self.ship.rigidbody.get_angle())
		if delta_angle>0:
			self.ship.rigidbody.rotate(self.ship.turn_rate)
		if delta_angle<0:
			self.ship.rigidbody.rotate(-self.ship.turn_rate)

class ConstrainByDamageSystemStatus(ai.AIItemHint):
	def get_suggested(self, ai):
		system=ai.ship.targeted.damage.search_system(dget(self.config, "search_name", None), dget(self.config, "search_key", None))
		translate={
			"optimal":0,
			"damaged":1,
			"destroyed":2
		}
		if system:
			print str(system.name)+" "+str(system.status)+" "+str(system.health)
			# print "vs"

			if "exactly" in self.config.keys():
				# print "e"+str(translate[self.config["exactly"]])
				if system.status==translate[self.config["exactly"]]:
					return True
			if "below" in self.config.keys():
				# print "b"+str(translate[self.config["below"]])
				if system.status>translate[self.config["below"]]:
					return True
			if "above" in self.config.keys():
				# print "a"+str(translate[self.config["above"]])
				if system.status<translate[self.config["above"]]:
					return True
			print 
		return False

def init_ais(root):
	ai.add_update_node(root, "select_player", SelectPlayer)
	ai.add_update_node(root, "point_at_selected", PointAtSelected)
	ai.add_hint_node(root, "constrain_by_system_damage", ConstrainByDamageSystemStatus)