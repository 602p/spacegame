import extention_loader, pygame
from logging import debug, info, warning, error, critical


class ClickHook(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if event.type==pygame.MOUSEBUTTONDOWN:
				self.root.gamedb.get_asset("x_sound_mousedown").play()

def init_inject(root, console):
	info("Injecting the SoundHook")
	extention_loader.safepost(console, "[eventsounds:sound_click]: Injecting the SoundHook", color=(0,255,255), bold=1)                                                                                           
	root.extentions["x_sounds_clickhook"]=ClickHook(root)