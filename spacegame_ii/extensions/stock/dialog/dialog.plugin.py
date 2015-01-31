import extention_loader, pygame
from logging import debug, info, warning, error, critical

class InteractionManager(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	
	def tick(self, state):
		if state=="game":
			if self.root.state_manager.states["game"].player.targeted:
				if pygame.key.get_pressed()[self.root.settings["keybindings"]["talk"]]:
					self.root.dialog_manager.start_dialog(
						self.root.state_manager.states["game"].player.targeted,
						self.root.state_manager.states["game"].player.targeted.config.get("dialog_topic", "greeting")
					)


def init_regwarps(root, _):
	root.extentions["dialog_interact_manager"]=InteractionManager(root)