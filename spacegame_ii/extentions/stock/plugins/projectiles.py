import primitives, physics, assets, pygame, random
from rotutil import rot_center
from jsonutil import dget
from particles import Particle

class Projectile:
	def __init__(self, image, root, parent, lifetime, homing, velocity, impact):
		self.rigidbody=physics.RigidBody2D(1, parent.get_center()[0], parent.get_center()[1],
			physics.Vector2d(velocity, parent.parent.rigidbody.get_angle()))
		self.homing=homing
		self.impact=impact
		self.lifetime=lifetime
		self.currtime=0
		self.image=image
		self.kill=False
		self.root=root
		self.parent=parent
		self.name="PROJECTILE"

		self.can_be_hit=False

	def tick(self, screen, time):
		self.currtime+=time
		self.rotated_image, self.rotated_rect=rot_center(self.image.copy(), pygame.Rect((self.rigidbody.x, self.rigidbody.y), self.image.get_size()), self.rigidbody.get_angle())
		screen.blit(self.rotated_image, (self.rotated_rect.x,self.rotated_rect.y))
		self.rigidbody.update_in_seconds(time)
		if self.currtime>self.lifetime:
			self.kill=True
		for i in self.root.state_manager.states["game"].entities:
			if i != self.parent.parent and i.can_be_hit:
				if i.rotated_rect.collidepoint((self.rigidbody.x, self.rigidbody.y)):
					self.kill=True
					self.impacted=i
					for i in self.impact:
						if not primitives.run_primitive(self.root, i["primitive"], i, self): break

def gen_explosion_from_node_source(n, x, y):
	i=0
	ps=[]
	while i<dget(n, "particles", 200):
		surf=pygame.Surface((dget(n, "size", 2), dget(n, "size", 2)))
		surf.fill((random.randint(dget(n, "r_min", 200), dget(n, "r_max", 255)), random.randint(dget(n, "g_min", 150), dget(n, "g_max", 200)), 0))
		exec("""def move_direction(self):
	self.x+="""+str((random.random()-random.random())*dget(n, "speed", 3))+"""
	self.y+="""+str((random.random()-random.random())*dget(n, "speed", 3)))
		ps.append(Particle(surf, x, y, move_direction, random.randint(dget(n, "time_min", 15), dget(n, "time_max", 45)), True))
		i+=1
	return ps

def init_primitives(root):
	def fire_projectile(r, n, p):
		r.state_manager.states["game"].entities.append(Projectile(r.gamedb.get_asset(n["image"]), r,
			p, n["lifetime"], n["homing"], n["velocity"], n["impact"]))
		return True
	primitives.register_primitive(root, "fire_projectile", fire_projectile)

	def simple_damage_impact(r, n, p):
		if "peirce" in n:
			peirce=n["peirce"]
		else:
			peirce=0
		p.impacted.damage(n["damage"], peirce)
		return True
	primitives.register_primitive(root, "simple_damage_impact", simple_damage_impact)

	def explosion_at_parent_targeted(r, n, p):
		p.impacted.particlemanager.add_particles(gen_explosion_from_node_source(n, p.rigidbody.x, p.rigidbody.y))
		return True
	primitives.register_primitive(root, "explosion_at_parent_targeted", explosion_at_parent_targeted)

	def sound_effect(r, n, p):
		r.gamedb.get_asset(n["effect"]).play()
		return True
	primitives.register_primitive(root, "sound_effect", sound_effect)