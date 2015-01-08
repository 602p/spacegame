import extention_loader, pygame, ui_states
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
	def last_load(self):
		debug("Adding WidgetControllers")
		self.root.state_manager.states["generic_ui"].widget_controllers["repair_player"]=RepairPlayerShip

class RepairPlayerShip(ui_states.WidgetController):
	def on_click(self):
		self.root.state_manager.states["game"].player.damage.hull=self.root.state_manager.states["game"].player.damage.maxhull
		for i in self.root.state_manager.states["game"].player.damage.systems:
			if i:
				i.deal_damage(-10000)

def init_inject(root):
	info("Injecting the CheatHook")
	root.extentions["cheathook"]=CheatHook(root)