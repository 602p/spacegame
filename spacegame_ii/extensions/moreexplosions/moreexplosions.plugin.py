import extention_loader, pygame, ui_states, triggers, primitives
from logging import debug, info, warning, error, critical

class ExplosionSFXManager(extention_loader.HookableExtention):
	name = "Explosion Manager"
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if event.type==pygame.USEREVENT:
			if event.sg_type==triggers.UE_HUL_DAMAGE_DEALT:
				debug("Got a UE_HUL_DAMAGE_DEALT event, playing sounds")
				primitives.do_group_for_impact(self.root, self.root.gamedb("x_moreexplosions_config"), None, None, None)

			#print "uevent --> "+str(event)
	def get_color(self):
		return (0,170,0)

	def get_italic(self):
		return 1

	def get_desc(self):
		return "Adds extra explosion noises"

def init_inject(root, console):
	info("Injecting the ExplosionHook")
	extention_loader.safepost(console, "[moreexplosions:ExplosionSFXManager]: Injecting the ExplosionHook", color=(0,255,255), bold=1)                                                                                           
	root.extentions["x_more_explosions"]=ExplosionSFXManager(root)