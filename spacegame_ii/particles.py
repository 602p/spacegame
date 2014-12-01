import pygame, random
from jsonutil import dget

class Particle(object):
	def __init__(self, root, surface, x, y, update, dieoff, collidekill=False):
		self.dieoff=dieoff
		self.start=root.game_time
		self.x=x
		self.y=y
		self.surface=surface
		self.delete=False
		self._update=update
		self.collidekill=collidekill
		self.root=root

	def update(self):
		self._update(self)
		if self.root.game_time-self.start>self.dieoff:
			self.delete=True

	def draw(self, surface):
		surface.blit(self.surface, (self.x, self.y))

def _update_float_up(self):
	self.y-=1

def make_floater(r, x, y, color):
	surf=pygame.Surface((1,1))
	surf.fill(color)
	return Particle(r, surf, x, y, lambda s:0, 0.1)

def make_hitNumber(number, font, x, y):
	return make_hitText(str(number), font, x, y, (255, 0, 0))

def make_hitText(text, font, x, y, color):
	return Particle(font.render(text, False, color), x, y, _update_float_up, 60)

def make_explosion(root, x, y, count=200):
	i=0
	ps=[]
	while i<count:
		surf=pygame.Surface((2,2))
		surf.fill((random.uniform(200, 255), random.uniform(200, 230), 0))
		exec("""def move_direction(self):
	self.x+="""+str((random.random()-random.random())*3)+"""
	self.y+="""+str((random.random()-random.random())*3))
		ps.append(Particle(root, surf, x, y, move_direction, 45, True))
		i+=1
	return ps

def make_gibs(root, x, y, num=50):
	i=0
	ps=[]
	while i<=num:
		surf=pygame.Surface((2,2))
		surf.fill((random.uniform(150, 255), 0, 0))
		exec("""def move_direction(self):
	self.x+="""+str((random.random()-random.random())*2)+"""
	self.y+="""+str((random.random()-random.random())*2))
		ps.append(Particle(surf, x, y, move_direction, random.uniform(10,30), True))
		i+=1
	return ps

def make_explosion_cfg(r, x, y, n):
	i=0
	ps=[]
	while i<dget(n, "particles", 200):
		surf=pygame.Surface((int(random.uniform(dget(n, "size_min", 2), dget(n, "size_max", 2))), int(random.uniform(dget(n, "size_min", 2), (dget(n, "size_max", 2))))))
		surf.fill((random.uniform(dget(n, "r_min", 200), dget(n, "r_max", 255)), random.uniform(dget(n, "g_min", 150), dget(n, "g_max", 200)), random.uniform(dget(n, "b_min", 0), dget(n, "b_max", 0))))
		exec("""def move_direction(self):
	self.x+="""+str((random.random()-random.random())*(random.uniform(dget(n, "speed_min", 3), dget(n, "speed_max", 3))))+"""
	self.y+="""+str((random.random()-random.random())*(random.uniform(dget(n, "speed_min", 3), dget(n, "speed_max", 3)))))
		ps.append(Particle(r, surf, x, y, move_direction, random.uniform(dget(n, "time_min", 15), dget(n, "time_max", 45)), True))
		i+=1
	return ps

class ParticleManager(object):
	def __init__(self):
		self.particles=[]

	def add_particle(self, particle):
		self.particles.append(particle)

	def add_particles(self, particles):
		self.particles.extend(particles)

	def update(self, collision=[]):
		for i in self.particles:
			i.update()
			if i.collidekill:
				for c in collision:
					if c.collidepoint(i.x, i.y):
						i.delete=True
			if i.delete:
				del self.particles[self.particles.index(i)]

	def draw(self, screen):
		for i in self.particles:
			i.draw(screen)