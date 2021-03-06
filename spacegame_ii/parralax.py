from __future__ import division
import pygame, random
import logging
module_logger=logging.getLogger("sg.parralax")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


class StarfieldLayer:
	def __init__(self, density, color, size, speed):
		self.density=density
		self.speed=speed

		self.particle_surface=pygame.Surface((size, size))
		self.particle_surface.fill(color)

	def bind(self, (xsize, ysize)):
		self.particles=[]
		self.size=(xsize, ysize)

	def render(self, surface, (xpos, ypos)):
		i=0
		state=random.getstate()
		random.seed(413)
		while i!=self.density:
			#
			pos=(random.uniform(0, self.size[0]), random.uniform(0, self.size[1]))
			surface.blit(self.particle_surface,
				(
					int((((xpos+pos[0])/self.speed)%self.size[0])),
					int((((ypos+pos[1])/self.speed)%self.size[1]))
				)
				)
			i+=1
		random.setstate(state)

class ParralaxStarfieldScroller:
	def __init__(self, size, layers):
		self.layers=layers
		self.pos=[0,0]
		self.bindall(size)
		debug("Initilized ParralaxStarfieldScroller with "+str(len(layers))+" layers at []:"+str(size))
	
	def bindall(self, size):
		for layer in self.layers:
			layer.bind(size)

	def render(self, surface):
		for layer in self.layers:
			layer.render(surface, self.pos)

	def move(self, x, y):
		self.pos[0]+=x
		self.pos[1]+=y

	def move_to(self, x, y):
		self.pos[0]=x
		self.pos[1]=y