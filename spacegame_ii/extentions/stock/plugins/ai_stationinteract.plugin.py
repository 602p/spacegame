import ai, pygame
from logging import debug, info, warning, error, critical

class InteractableToEnterStation(ai.AIControllerUpdateNode):
	def init(self):
		self.cooldown_last=0
	def update(self):
		if pygame.key.get_pressed()[self.controller.root.settings["keybindings"]["interact"]]:
			if self.controller.gamestate.player.rotated_mask.overlap(self.ship.rotated_mask,
					(self.ship.rotated_rect.x-self.controller.gamestate.player.rotated_rect.x,
					self.ship.rotated_rect.y-self.controller.gamestate.player.rotated_rect.y)) or 1:
				if self.controller.gamestate.player.rigidbody.moving()<50:
					debug("Entering station")
					self.controller.gamestate.player.rigidbody.set_magnitude(0)
					self.controller.root.state_manager.start_interdicting("generic_ui", self.config["station_cfg"])
				else:
					if self.controller.root.game_time-self.cooldown_last>4:
						self.controller.root.igconsole.post("Please slow down before docking", (0,255,0), bold=True)
						self.cooldown_last=self.controller.root.game_time

def init_ais(root):
	ai.add_update_node(root, "spacestation", InteractableToEnterStation)