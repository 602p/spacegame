import ai, math
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
		return False

class FollowSelected(ai.AIControllerUpdateNode):
	def update(self):
		delta_angle=get_rel_angle(get_angle(self.ship.rotated_rect.center[0], self.ship.targeted.rotated_rect.center[0],
			self.ship.rotated_rect.center[1], self.ship.targeted.rotated_rect.center[1]), self.ship.rigidbody.get_angle())
		if abs(delta_angle)<45:
			if "trail_distance" in self.config.keys():
				if abs(math.hypot(self.ship.rotated_rect.center[0]-self.ship.targeted.rotated_rect[0], 
					self.ship.rotated_rect.center[1]-self.ship.targeted.rotated_rect[1]))>self.config["trail_distance"]:
					self.ship.exert_engine()
				else:
					self.ship.exert_reverse_engine()
			else:
				self.ship.exert_engine()
		else:
			self.ship.exert_reverse_engine()

class ConstrainByShipAttribute(ai.AIItemHint):
	def get_suggested(self, ai):
		attr=eval("ai.ship.targeted."+self.config["attribute"])
		if "exactly" in self.config.keys():
			if attr==self.config["exactly"]:
				return True

		if "below" in self.config.keys():
			if attr<self.config["below"]:
				return True

		if "above" in self.config.keys():
			if attr>self.config["above"]:
				return True
		return False


def init_ais(root, console):
	ai.add_update_node(root, "select_player", SelectPlayer)
	ai.add_update_node(root, "point_at_selected", PointAtSelected)
	ai.add_update_node(root, "follow_selected", FollowSelected)
	ai.add_hint_node(root, "constrain_by_system_damage", ConstrainByDamageSystemStatus)
	ai.add_hint_node(root, "constrain_by_attribute_status", ConstrainByShipAttribute)