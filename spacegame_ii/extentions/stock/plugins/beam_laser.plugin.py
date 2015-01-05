import primitives, tasks, particles
from jsonutil import dget

class RenderLaserBeamPrimitive(primitives.BasePrimitive):
	def run_in_item(self, item):
		def _internal(t, r):
			p=t.data[1]
			n=t.data[0]
			try:
				r.screen.draw_line(n["color"], t.data[1].get_center(), t.data[1].parent.targeted.rotated_rect.center, n["thickness"])
			except BaseException:
				pass
		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internal, self.config["duration"], (self.config, item)))

class ExplosionAtPrimitive(primitives.BasePrimitive):
	def run_in_item(self, item):
		if dget(self.config, "root", False):
			self.root.particlemanager.add_particles(particles.make_explosion_cfg(self.root,
				item.parent.rotated_rect.center[0], item.parent.rotated_rect.center[1], self.config["style"]))
		else:
			item.parent.particlemanager.add_particles(particles.make_explosion_cfg(self.root,
				item.parent.rotated_rect.center[0], item.parent.rotated_rect.center[1], self.config["style"]))

	def run_in_impact(self, item, impacted):
		if dget(self.config, "root", False):
			self.root.particlemanager.add_particles(particles.make_explosion_cfg(self.root,
				impacted.rotated_rect.center[0], impacted.rotated_rect.center[1], self.config["style"]))
		else:
			impacted.particlemanager.add_particles(particles.make_explosion_cfg(self.root,
				impacted.rotated_rect.center[0], impacted.rotated_rect.center[1], self.config["style"]))

	def run_in_ship(self, ship):
		if dget(self.config, "root", False):
			self.root.particlemanager.add_particles(particles.make_explosion_cfg(self.root,
				ship.rotated_rect.center[0], ship.rotated_rect.center[1], self.config["style"]))
		else:
			ship.particlemanager.add_particles(particles.make_explosion_cfg(self.root,
				ship.rotated_rect.center[0], ship.rotated_rect.center[1], self.config["style"]))

def init_primitives(root):
	primitives.register_primitive(root, "render_laser_beam_targeted", RenderLaserBeamPrimitive)

	primitives.register_primitive(root, "explosion_at_parent", ExplosionAtPrimitive)
