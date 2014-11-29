import pygame, random



class Particle(object):
	def __init__(self, surface, x, y, update, dieoff, collidekill=False):
		self.dieoff=dieoff
		self.currtick=0
		self.x=x
		self.y=y
		self.surface=surface
		self.delete=False
		self._update=update
		self.collidekill=collidekill

	def update(self):
		self._update(self)
		self.currtick+=1
		if self.currtick==self.dieoff:
			self.delete=True

	def draw(self, surface):
		surface.blit(self.surface, (self.x, self.y))

def _update_float_up(self):
	self.y-=1

def make_floater(x, y, color):
	surf=pygame.Surface((1,1))
	surf.fill(color)
	return Particle(surf, x, y, lambda s:0, 15)

def make_hitNumber(number, font, x, y):
	return make_hitText(str(number), font, x, y, (255, 0, 0))

def make_hitText(text, font, x, y, color):
	return Particle(font.render(text, False, color), x, y, _update_float_up, 60)

def make_explosion_pix(x, y):
	i=0
	ps=[]
	while i<201:
		surf=pygame.Surface((2,2))
		surf.fill((random.randint(150, 255), random.randint(0, 100), 0))
		exec("""def move_direction(self):
	self.x+="""+str((random.random()-random.random())*6)+"""
	self.y+="""+str((random.random()-random.random())*6))
		ps.append(Particle(surf, x, y, move_direction, 45, True))
		i+=1
	return ps

def make_gibs(x, y, num=50):
	i=0
	ps=[]
	while i<=num:
		surf=pygame.Surface((2,2))
		surf.fill((random.randint(150, 255), 0, 0))
		exec("""def move_direction(self):
	self.x+="""+str((random.random()-random.random())*2)+"""
	self.y+="""+str((random.random()-random.random())*2))
		ps.append(Particle(surf, x, y, move_direction, 15, True))
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