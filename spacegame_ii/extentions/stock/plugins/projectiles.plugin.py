import primitives, physics, assets, pygame, random, math, cmath
from rotutil import rot_center, get_angle, get_rel_angle, rotate_point
from jsonutil import dget
from particles import Particle

class Projectile:
	def __init__(self, image, root, parent, lifetime, homing, velocity, impact, maxspeed, accel, particlestyle={"particles":0}, turnrate=60, offset_min=0, offset_max=0, cfg={}):
		self.rigidbody=physics.RigidBody2D(1, parent.get_center()[0]+random.uniform(offset_min, offset_max),
		    parent.get_center()[1]+random.uniform(offset_min, offset_max),physics.Vector2d(velocity, parent.parent.rigidbody.get_angle()))
		self.homing=homing
		self.impact=impact
		self.lifetime=lifetime
		self.currtime=0
		self.image=image
		self.mask=pygame.mask.from_surface(self.image)
		self.particlemanager=particles.ParticleManager()
		self.kill=False
		self.root=root
		self.start=self.root.game_time
		self.parent=parent
		self.name="PROJECTILE"
		self.maxspeed=maxspeed
		self.accel=accel
		self.particlestyle=particlestyle
		self.turnrate=turnrate
		self.targeted = None #So we don't spam the log with "Projectile instance has no attribute 'targeted'""
		if self.homing:
			self.targeted=self.parent.parent.targeted

		self.can_be_hit=False
		self.config=cfg
		self.oldangle=-100000

		self.rerotate()
		self.rotated_mask=pygame.mask.from_surface(self.rotated_image)

	def rerotate(self):
		self.rotated_image, self.rotated_rect=rot_center(self.image.copy(), pygame.Rect((self.rigidbody.x, self.rigidbody.y), self.image.get_size()), self.rigidbody.get_angle())

	def tick(self, screen, time):
		self.currtime+=time
		
		if int(self.oldangle)!=self.rigidbody.get_angle():
			self.rerotate()
			self.oldangle=self.rigidbody.get_angle()
		screen.blit(self.rotated_image, (self.rigidbody.x, self.rigidbody.y))

		self.rigidbody.update_in_seconds(time)
		self.rigidbody.exert_in_vector(self.accel, cap=self.maxspeed)
		self.particlemanager.update()
		self.particlemanager.draw(self.root.screen)
		x_=self.rotated_rect.centerx
		y_=self.rotated_rect.centery
		if "particle_offset" in self.config.keys():
			x_, y_ = rotate_point(self.rotated_rect.center, (
				self.config["particle_offset"][0]+self.rigidbody.x, self.config["particle_offset"][1]+self.rigidbody.y) ,
				-self.rigidbody.get_angle())

		self.particlemanager.add_particles(particles.make_explosion_cfg(self.root, x_, y_, self.particlestyle))

		if self.homing and self.targeted:
			# rel_angle=math.degrees(math.atan2(self.targeted.rotated_rect.center[1]-self.rotated_rect.center[1],
			#  -(self.targeted.rotated_rect.center[0]-self.rotated_rect.center[0])))+90
			# delta_angle=math.degrees(math.atan2(
			# 	math.sin(math.radians(rel_angle)-math.radians(self.rigidbody.get_angle())),
			# 	math.cos(math.radians(rel_angle)-math.radians(self.rigidbody.get_angle()))
			# ))
			delta_angle=get_rel_angle(get_angle(self.rotated_rect.center[0], self.targeted.rotated_rect.center[0],
				self.rotated_rect.center[1], self.targeted.rotated_rect.center[1]), self.rigidbody.get_angle())
			if delta_angle>0:
				self.rigidbody.rotate(self.turnrate)
			if delta_angle<0:
				self.rigidbody.rotate(-self.turnrate)


		if self.root.game_time-self.start>self.lifetime:
			self.kill=True
		for i in self.root.state_manager.states["game"].entities:
			if i != self.parent.parent and i.can_be_hit:
				if i.rotated_mask.overlap(self.mask, (self.rotated_rect.x-i.rotated_rect.x,self.rotated_rect.y-i.rotated_rect.y)):
					self.kill=True
					primitives.do_group_for_impact(self.root, self.impact, self.parent, i, self)

	def die(self):
		pass

class FireProjectilePrimitive(primitives.BasePrimitive):
	def run_in_item(self, item):
		n=self.config
		r=self.root
		i=0
		while i!=dget(n, "number", 1):
			r.state_manager.states["game"].entities.append(Projectile(r.gamedb.get_asset(n["image"]), r,
				item, n["lifetime"], n["homing"], n["velocity"], n["impact"], n["maxspeed"], n["accel"], dget(n, "particlestyle", {"particles":0}), dget(n, "turnrate", 60),
				dget(n, "offset_min", 0), dget(n, "offset_max", 0), n))
			i+=1

class SimpleDamagePrimitive(primitives.BasePrimitive):
	def do(root, target, px, py):
		target.damage(root.config["damage"], dget(root.config, "peirce", 0), px, py)

	def run_in_item(self, item):
		self.do(item.parent.targeted, None, None)

	def run_in_impact(self, item, impacted, projectile):
		self.do(impacted, projectile.rotated_rect.centerx, projectile.rotated_rect.centery)

class SystemDamagePrimitive(primitives.BasePrimitive):
	def run_in_impact(self, item, impacted, projectile):
		impacted.damage.damage_system(self.config["damage"], dget(self.config, "system_name", None), dget(self.config, "system_key", None))

	def run_in_item(self, item):
		item.parent.targeted.damage.damage_system(self.config["damage"], dget(self.config, "system_name", None), dget(self.config, "system_key", None))

class PlaySoundEffectPrimitive(primitives.BasePrimitive):
	def do(self):
		self.root.gamedb.get_asset(self.config["effect"]).play()

	def run_in_impact(self, item, impacted, projectile):
		self.do()

	def run_in_item(self, item):
		self.do()

def init_primitives(root):
	primitives.register_primitive(root, "fire_projectile", FireProjectilePrimitive)

	primitives.register_primitive(root, "simple_damage", SimpleDamagePrimitive)

	primitives.register_primitive(root, "system_damage", SystemDamagePrimitive)

	primitives.register_primitive(root, "sound_effect", PlaySoundEffectPrimitive)