import extention_loader, pygame, ui_states, triggers, primitives
from logging import debug, info, warning, error, critical

class ExplosionSFXManager(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if event.type==pygame.USEREVENT:
			if event.sg_type==triggers.UE_PROJECTILE_IMPACT:
				debug("Got a UE_PROJECTILE_IMPACT event, playing sounds")
				primitives.do_group_for_impact(self.root, self.root.gamedb("x_moreexplosions_config"),
				 event.projectile.parent, event.hit, event.projectile)
			#print "uevent --> "+str(event)

def init_inject(root, console):
	info("Injecting the ExplosionHook")
	extention_loader.safepost(console, "[moreexplosions:ExplosionSFXManager]: Injecting the ExplosionHook", color=(0,255,255), bold=1)                                                                                           
	root.extentions["x_more_explosions"]=ExplosionSFXManager(root)