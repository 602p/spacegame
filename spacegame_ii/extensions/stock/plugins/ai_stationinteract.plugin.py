import ai, pygame
from logging import debug, info, warning, error, critical

class InteractableToEnterStation(ai.AIControllerUpdateNode):
	def init(self):
		self.cooldown_last=0
	def update(self):
		#print "updated"
		if pygame.key.get_pressed()[self.controller.root.settings["keybindings"]["interact"]]:
			#print "pressed"
			if self.controller.gamestate.player.rotated_mask.overlap(self.ship.rotated_mask,
					(self.ship.rotated_rect.x-self.controller.gamestate.player.rotated_rect.x,
					self.ship.rotated_rect.y-self.controller.gamestate.player.rotated_rect.y)) or 0:
				#print "collided"
				if self.controller.gamestate.player.rigidbody.moving()<self.config.get("max_speed", 75):
					debug("Entering station")
					self.controller.gamestate.player.rigidbody.set_magnitude(0)
					self.config["ui_config"]["bg_image"]=self.config["bg_image"]
					state=self.controller.root.state_manager.start_interdicting("generic_ui", self.config["ui_config"])
					debug("Patching State")
					patch_text_kit={
						"station_name":self.config.get("name", "UNSET NAME")
					}
					for widget_k in state.widgets:
						widget=state.widgets[widget_k]
						if "text" in widget._json_config.keys():
							widget.config(text=widget._json_config["text"] % patch_text_kit)
						widget._switch()
				else:
					if self.controller.root.game_time-self.cooldown_last>4:
						self.controller.root.igconsole.post("Please slow down before docking", (0,255,0), bold=True)
						self.cooldown_last=self.controller.root.game_time

def init_ais(root, console):
	ai.add_update_node(root, "spacestation", InteractableToEnterStation)