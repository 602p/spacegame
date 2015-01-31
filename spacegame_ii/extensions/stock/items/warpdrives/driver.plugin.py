from __future__ import division
import item, extention_loader, pygame, particles, tasks

from logging import debug, info, warning, error, critical

class WarpdriveItemFactory(item.ItemFactory):
	def __call__(self, p, e):
		debug("Creating a "+self.config["id"]+" using WarpdriveItemFactory")
		return WarpDriveItem(self.root, e, p, self.config)

class WarpDriveItem(item.Item):
	def __init__(self, *args, **kw):
		item.Item.__init__(self, *args, **kw)
		print self.fire_required
		self.xwd_is_charging=0
		self.xwd_charge_status=0
		self.xwd_warp_factor=self.config["xwd_warp_factor"]
		self.xwd_charge_power=self.config["xwd_charge_power"]
		self.xwd_charge_shield=self.config["xwd_charge_shield"]
		self.xwd_charge_time=self.config["xwd_charge_time"]
		self.xwd_warp_color=self.config["warp_color"]
		self.xwd_at_warp=0

	def fire_actions(self):
		item.Item.fire_actions(self)
		self.xwd_is_charging=not self.xwd_is_charging
		debug("Toggled charging... is now "+str(self.xwd_is_charging))

		if self.xwd_charge_status>=self.xwd_charge_time and not self.xwd_at_warp:
			self.do_screen_flash()
		elif self.xwd_at_warp:
			self.xwd_charge_status=0
			self.xwd_is_charging=0
			self.xwd_at_warp=0
			#self.parent.rigidbody._vector.magnitude=40
			self.parent.max_speed=self.xwd_orig_speed
			self.do_screen_flash_end()

	def do_screen_flash(self):
		DURATION=0.4
		EXPONENT=2.2
		def _internal(t, r):
			surf=pygame.Surface((1300,700))
			surf.fill(pygame.Color(255,255,255))
			surf.set_alpha((t.curr_time**EXPONENT)*(255/DURATION**EXPONENT))
			r.screen.screen.blit(surf, (0,0))
		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internal, DURATION))
		def _internalt(t, r):
			self=t.data
			if t.delete:
				self.xwd_charge_status=0
				self.xwd_is_charging=0
				self.xwd_at_warp=1
				self.xwd_orig_speed=self.parent.max_speed
				self.parent.max_speed*=self.xwd_warp_factor
				self.parent.rigidbody._vector.magnitude=self.parent.max_speed
		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internalt, DURATION, self))

	def do_screen_flash_end(self):
		DURATION=0.4
		EXPONENT=2.2
		def _internal(t, r):
			surf=pygame.Surface((1300,700))
			surf.fill(pygame.Color(255,255,255))
			surf.set_alpha(255-((t.curr_time**EXPONENT)*(255/DURATION**EXPONENT)))
			r.screen.screen.blit(surf, (0,0))
		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internal, DURATION))

	def update(self, dt):
		if self.xwd_is_charging:
			self.xwd_charge_status+=dt
			if self.xwd_charge_status>=self.xwd_charge_time:
				self.xwd_is_charging=0
			self.parent.current_power=min(self.parent.reactor_max*self.xwd_charge_power, self.parent.current_power)
			self.parent.damage.shields=min(self.parent.damage.maxshields*self.xwd_charge_shield, self.parent.damage.shields)
		elif self.xwd_at_warp:
			self.parent.rigidbody._vector.magnitude=self.parent.max_speed
			#self.parent.particlemanager.add_particles(particles.make_warptrail(self.root, self.parent.rigidbody.x, self.parent.rigidbody.y, self.xwd_warp_color))

	def get_inventory_image(self):
		surface=item.Item.get_inventory_image(self)
		pygame.draw.rect(surface, (0,255,0), pygame.Rect(0, 58, min((self.xwd_charge_status/self.xwd_charge_time)*64, 64), 6))
		return surface

	def save_to_config_node(self):
		cfg=item.Item.save_to_config_node(self)
		cfg.update({
			"xwd_charge_status":self.xwd_charge_status,
			"xwd_is_charging":self.xwd_is_charging,
			"xwd_at_warp":self.xwd_at_warp
		})
		return cfg

	def do_additional_load(self, config):
		self.xwd_charge_status=config.get("xwd_charge_status", 0)
		self.xwd_is_charging=config.get("xwd_is_charging", 0)
		if config.get("xwd_at_warp", 0):
			self.xwd_charge_status=99999999
			self.fire_actions()

class WarpDriveManager(extention_loader.HookableExtention):
	def __init__(self, root, console):
		self.root=root
		self.console=console
	def after_items_load(self):
		for asset_cfg in self.root.gamedb.get_startswith("warpdriveloader_"):
			extention_loader.safepost(self.console, "Loading Item from assetkey:"+asset_cfg["id"]+" with WarpdriveItemFactory...")
			self.root.item_factories[asset_cfg["id"]]=WarpdriveItemFactory(self.root, asset_cfg)


def init_regwarps(root, _):
	root.extentions["warp_drive_manager"]=WarpDriveManager(root, _)