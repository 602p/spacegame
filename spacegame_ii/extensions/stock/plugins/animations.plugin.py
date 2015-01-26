import primitives, pyganim, tasks, random

class RenderAnimationPrimitive(primitives.BasePrimitive):
	def run_in_impact(self, item, impacted, projectile):
		def _internal(t, r):
			t.data[0].blit(r.screen, (t.data[1][0], t.data[1][1]))
		built_array=[]
		for i in self.config["style"]["frames"]:
			built_array.append([self.root.gamedb(i[0]),i[1]])
		animation = pyganim.PygAnimation(built_array, loop=0)
		animation.play()
		x = projectile.rigidbody.x-self.config["style"].get("offset",[0,0])[0]
		y = projectile.rigidbody.y-self.config["style"].get("offset",[0,0])[1]
		tasks.add_task(self.root, "render_after_entities", tasks.Task(self.root, _internal,
			self.config["style"]["sum_duration"], (animation, [x,y])))
	def run_in_ship(self, ship):
		self.run_in_impact(None, None, ship)

class DelayedAnimationPrimitive(primitives.BasePrimitive):
	def run_in_ship(self, ship):
		#print "called in ship"
		def _internalab(t, r):
			t.data[0].play()
			t.data[0].blit(r.screen, (t.data[1][0], t.data[1][1]))
		def _internalde(t,r):
			if t.delete:
				tasks.add_task(self.root, "render_after_entities", tasks.Task(self.root, _internalab,
					self.config["style"]["sum_duration"], t.data))

		ax=ship.rotated_rect.centerx+random.choice(xrange(int(-ship.rotated_rect.size[0]/2), int(ship.rotated_rect.size[0]/2)))-self.config["style"].get("offset",[0,0])[0]
		ay=ship.rotated_rect.centery+random.choice(xrange(int(-ship.rotated_rect.size[1]/2), int(ship.rotated_rect.size[1]/2)))-self.config["style"].get("offset",[0,0])[1]

		built_array=[]
		for i in self.config["style"]["frames"]:
			built_array.append([self.root.gamedb(i[0]),i[1]])
		animation = pyganim.PygAnimation(built_array, loop=0)
		#animation.play()

		tasks.add_task(self.root, "render_last", tasks.Task(self.root, _internalde, self.config["time"], (
			animation, [ax,ay])))

class EnsureRandomnessPrimitive(primitives.BasePrimitive):
	def do(self):
		random.seed(self.root.game_time*82)

	def run_in_impact(self, item, impacted, projectile):
		self.do()

	def run_in_item(self, item):
		self.do()

def init_primitives(root,console):
	primitives.register_primitive(root, "play_animation", RenderAnimationPrimitive)
	primitives.register_primitive(root, "play_animation_dr", DelayedAnimationPrimitive)
	primitives.register_primitive(root, "erandom", EnsureRandomnessPrimitive)