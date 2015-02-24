import extention_loader, absroot, tasks, pygame, rotutil, triggers, particles
from rotutil import *
from logging import debug, info

clamp = lambda my_value, min_value, max_value: max(min(my_value, max_value), min_value)

class ShieldFXManager(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if event.type==pygame.USEREVENT:
			if event.sg_type==triggers.UE_SHL_DAMAGE_DEALT:
				if not event.x:
					event.x, event.y = event.source.rotated_rect.center

				# dx =  - event.source.rotated_rect.centerx - event.x
				# dy =  - event.source.rotated_rect.centery - event.y
				
				angle=get_angle(event.system.ship.rotated_rect.centerx, event.x, 
					event.system.ship.rotated_rect.centery, event.y)

				orig_image=pygame.transform.scale(absroot.gamedb("image_shield_hit_default"), (event.system.ship.rotated_rect.width+100, event.system.ship.rotated_rect.height+100 ) )


				def _(t, r):
					orig_rect=pygame.Rect( (0,0), orig_image.get_size())
					orig_rect.center=(event.system.ship.rotated_rect.centerx,
						event.system.ship.rotated_rect.centery)

					rot_image, rot_rect=rot_center(orig_image, orig_rect, angle)
					absroot.screen.blit(rot_image, rot_rect)

				tasks.add_task(self.root, "render_after_entities", tasks.Task(absroot, _, 2))


def init_inject(root, console):
	info("Injecting the ShieldHook")
	extention_loader.safepost(console, "[ShieldFXManager]: Injecting the ShieldHook", color=(0,255,255), bold=1)                                                                                           
	root.extentions["shield_fx"]=ShieldFXManager(root)