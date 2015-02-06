import ai, pygame, item
from logging import debug, info, warning, error, critical

class InteractToGiveItems(ai.AIControllerUpdateNode):
	def init(self):
		self.cooldown_last=0
		self.has_run=0
	def update(self):
		#print "updated"
		if not self.has_run:
			if pygame.key.get_pressed()[self.controller.root.settings["keybindings"]["interact"]]:
				#print "pressed"
				if self.controller.gamestate.player.rotated_mask.overlap(self.ship.rotated_mask,
						(self.ship.rotated_rect.x-self.controller.gamestate.player.rotated_rect.x,
						self.ship.rotated_rect.y-self.controller.gamestate.player.rotated_rect.y)) or 0:
					#print "collided"
					if self.controller.gamestate.player.rigidbody.moving()<self.config.get("max_speed", 75):
						#print "doing"
						debug("Interacting w/ pod")
						#print "ip"
						try:
							for item in self.ship.inventory:
								self.controller.root.state_manager.states["game"].player.pick_up(item)
						except BaseException as e:
							print "ERROR!!!!LSAJDFOIAJDF"
							print e
						#print "ia"
						self.ship.damage(999999999)
						self.has_run=1
						#print "td"
					else:
						if self.controller.root.game_time-self.cooldown_last>4:
							self.controller.root.igconsole.post("Please slow down before docking", (255,255,0))
							self.cooldown_last=self.controller.root.game_time

def init_ais(root, console):
	ai.add_update_node(root, "cargopod", InteractToGiveItems)