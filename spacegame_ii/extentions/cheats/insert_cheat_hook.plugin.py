import extention_loader, pygame
from logging import debug, info, warning, error, critical

KEY_CODE=pygame.K_F10

class CheatHook(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if state=="game":
			if event.type==pygame.KEYDOWN:
				if event.key==KEY_CODE:
					self.root.state_manager.start_interdicting("generic_ui", self.root.gamedb("x_cheats_gui"))

def init_inject(root):
	info("Injecting the CheatHook")
	root.extentions["cheathook"]=CheatHook(root)