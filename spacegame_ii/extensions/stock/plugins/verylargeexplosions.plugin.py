from __future__ import division
import primitives, particles, random, tasks

class AfterImagePrimitive(primitives.BasePrimitive):
	def run_in_ship(self, ship):
		def _internal(t, r):
			r.screen.blit(t.data[1], t.data[0])
		tasks.add_task(self.root, "render_before_particles",
			tasks.Task(self.root, _internal, self.config["time"], (ship.rotated_rect.copy(), ship.rotated_image.copy())))

class DelayedExplosionPrimitive(primitives.BasePrimitive):
	def run_in_ship(self, ship):
		def _internalde(t,r):
			if t.delete:
				t.root.particlemanager.add_particles(particles.make_explosion_cfg(t.root,
					t.data[0], t.data[1], t.data[2]))

		ax=ship.rotated_rect.centerx+random.choice(xrange(int(-ship.rotated_rect.size[0]/2), int(ship.rotated_rect.size[0]/2)))
		ay=ship.rotated_rect.centery+random.choice(xrange(int(-ship.rotated_rect.size[1]/2), int(ship.rotated_rect.size[1]/2)))

		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internalde, self.config["time"], (
			ax,
			ay,
			self.config["style"])))

class DelayedSoundPrimitive(primitives.BasePrimitive):
	def run(self):
		def _internalsx(t,r):
			if t.delete:
				r.gamedb.get_asset(t.data).play()
		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internalsx, self.config["time"], self.config["sound"]))

	def run_in_ship(self, ship):
		self.run()

	def run_in_item(self, item):
		self.run()

	def run_in_impact(self, im, it, ta):
		self.run()

def init_primitives(root, console):
	primitives.register_primitive(root, "afterimage", AfterImagePrimitive)
	primitives.register_primitive(root, "explosion_dr", DelayedExplosionPrimitive)
	primitives.register_primitive(root, "delayed_sound_effect", DelayedSoundPrimitive)