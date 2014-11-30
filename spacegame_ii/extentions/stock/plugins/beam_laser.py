import primitives, tasks

def init_primitives(root):
	def test(r, n, p):
		def _internal(t, r):
			p=t.data[1]
			n=t.data[0]
			r.screen.draw_line(n["color"], p.get_center(), p.parent.targeted.rotated_rect.center, n["thickness"])
		tasks.add_task(r, "render_last", tasks.Task(r, _internal, n["duration"], (n, p)))
		return True
	primitives.register_primitive(root, "render_laser_beam", test)

	def test2(r, n, p):
		p.parent.targeted.damage(n["damage"])
		return True
	primitives.register_primitive(root, "simple_damage", test2)