import primitives, tasks, particles

def init_primitives(root):
	def test(r, n, p):
		def _internal(t, r):
			p=t.data[1]
			n=t.data[0]
			try:
				r.screen.draw_line(n["color"], p.get_center(), p.parent.targeted.rotated_rect.center, n["thickness"])
			except BaseException:
				pass
		tasks.add_task(r, "render_last", tasks.Task(r, _internal, n["duration"], (n, p)))
		return True
	primitives.register_primitive(root, "render_laser_beam", test)

	def test2(r, n, p):
		p.parent.targeted.damage(n["damage"])
		return True
	primitives.register_primitive(root, "simple_damage", test2)

	def explosion_at_parent(r, n, p):
		p.parent.targeted.particlemanager.add_particles(particles.make_explosion_cfg(r, p.parent.targeted.rotated_rect.center[0], p.parent.targeted.rotated_rect.center[1], n["style"]))
		return True
	primitives.register_primitive(root, "explosion_at_parent_targeted", explosion_at_parent)

	def explosion_at_parent_rootmanager(r, n, p):
		r.particlemanager.add_particles(particles.make_explosion_cfg(r, p.rotated_rect.center[0], p.rotated_rect.center[1], n["style"]))
		return True
	primitives.register_primitive(root, "explosion_at_parent_at_top", explosion_at_parent_rootmanager)