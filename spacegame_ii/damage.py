from __future__ import division
import random, pygame
from rotutil import rot_center, aspect_scale

system_status=[
	[" OPTIMAL ",(0,255,0)],
	[" DAMAGED ",(255,255,0)],
	["DESTROYED",(255,0,0)]
]


class DamageSystem:
	def __init__(self, damage_model, config):
		self.damage_model=damage_model
		self.status=0
		self.name=config["name"]
		self.attributes=config["attributes"]
		self.effects_damaged=config["effects_damaged"]
		self.effects_destroyed=config["effects_destroyed"]
		self.health=config["health"]
		self.threshold=config["threshold_damaged"]
		self.update_olds()

	def update_olds(self):
		self.olds={}
		for i in self.attributes:
			self.olds[i]=eval("self.damage_model.ship."+i)
		self.reset()
		self.deal_damage(0)

	def deal_damage(self, damage):
		self.health-=damage
		if self.health<=0 and self.status!=2:
			self.reset()
			self.health=0
			self.do_destroyed()
		elif self.health<self.threshold and self.health>0 and self.status!=1:
			self.reset()
			self.do_damaged()
		elif self.status!=0 and self.health>self.threshold:
			self.reset()
		if self.health<=0:
			self.health=0

	def do_damaged(self):
		for i in self.attributes:
			exec "self.damage_model.ship."+i+"="+str(self.olds[i]*self.effects_damaged[self.attributes.index(i)])
		self.status=1

	def do_destroyed(self):
		for i in self.attributes:
			exec "self.damage_model.ship."+i+"="+str(self.olds[i]*self.effects_destroyed[self.attributes.index(i)])
		self.status=2

	def reset(self):
		for i in self.attributes:
			exec "self.damage_model.ship."+i+"="+str(self.olds[i])
		self.status=0

	def get_descriptor(self):
		return (self.name+":"+system_status[self.status][0]+" ["+str(int(self.health))+"]",system_status[self.status][1])

class DamageModel:
	def __init__(self, ship, hull=1, shields=0):
		self.hull=hull
		self.maxhull=hull
		self.shields=shields
		self.maxshields=shields
		self.ship=ship
		self.systems=[]

	def damage_hull(self, hull):
		self.hull-=hull
		if len(self.systems)>0:
			s=random.sample(self.systems,1)[0]
			if s:
				s.deal_damage(hull)
		if self.hull<0:
			self.hull=0
			self.ship.on_destroy()

	def damage_shields(self, shields):
		self.shields-=shields
		if self.shields<0:
			self.damage_hull(abs(self.shields)*0.8)
			self.shields=0

	def damage(self, damage, peirce=0):
		self.damage_shields(damage*(1-peirce))
		self.damage_hull(damage*peirce)

	def load_systems(self, config):
		"""Takes a list of dicts describing systems and adds them to its internal register.
		config - Loaded from JSON"""
		for i in config:
			self.systems.append(DamageSystem(self, i)) #Instanciate a DamageSystem
			self.systems.append(None) #Add a placeholder so there is only a 1/2 chance of damage going to a system

	def render_full(self, screen, font, x=0, y=0):
		"""Render a full view of system damage status
		screen - surface to render on
		font - font to use
		x, y - top left corner position"""
		screen.blit(font.render("SYSTEMS:", False, (255,255,255)), (x,y))
		i=1
		for s in self.systems:
			if s:
				screen.blit(font.render(str(i)+": "+s.get_descriptor()[0], False, s.get_descriptor()[1]), (x,y+(i*20)))
				i+=1

	def render_infobox(self, screen, font, x, y):
		"""Render a small view of the ship, its shields, hull, and energy
		screen - surface to render on
		font - font to use
		x, y - offset of top left corner of minimap BOX, not whole widget"""
		rotated_image, rotated_rect=rot_center(aspect_scale(self.ship.image, (50,50)), pygame.Rect((x+50-(self.ship.image.get_width()/2),y+50-(self.ship.image.get_height()/2)), self.ship.image.get_size()), self.ship.rigidbody.get_angle())
		screen.blit(rotated_image, (rotated_rect.x,rotated_rect.y))
		pygame.draw.rect(screen, (255,255,255), pygame.Rect(x,y,100,100), 4)
		pygame.draw.rect(screen, (255,0,0), pygame.Rect(x,y+100,(self.hull/self.maxhull)*100,20))
		r=font.render("HUL:"+str(int(self.hull))+"/"+str(int(self.maxhull)), False, (100,255,255))
		screen.blit(r, (x+50-(r.get_width()/2),y+100+10-(r.get_height()/2)))
		pygame.draw.rect(screen, (0,0,255), pygame.Rect(x,y-20,(self.shields/self.maxshields)*100,20))
		r=font.render("SHL:"+str(int(self.shields))+"/"+str(int(self.maxshields)), False, (0,175,175))
		screen.blit(r, (x+50-(r.get_width()/2),y-20+(r.get_height()/2)))
		pygame.draw.rect(screen, (0,255,0), pygame.Rect(x,y+120,(self.ship.current_power/self.ship.reactor_max)*100,20))
		r=font.render("PWR:"+str(int(self.ship.current_power))+"/"+str(int(self.ship.reactor_max)), False, (0,175,175))
		screen.blit(r, (x+50-(r.get_width()/2),y+120+10-(r.get_height()/2)))

	def regen(self):
		if self.shields<self.maxshields:
			if self.ship.current_power>2:
				self.shields+=2/self.ship.root.clock.get_fps()
				self.ship.current_power-=2/self.ship.root.clock.get_fps()

	def __call__(self, *args, **kwargs):
		self.damage(*args, **kwargs)