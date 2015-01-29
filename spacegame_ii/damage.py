from __future__ import division
import random, pygame, math, particles
from rotutil import rot_center, aspect_scale
from jsonutil import dget
from triggers import *

system_status=[
	[" OPTIMAL ",(0,255,0)],
	[" DAMAGED ",(255,255,0)],
	["DESTROYED",(255,0,0)]
]


class DamageSystem:
	def __init__(self, damage_model, config):
		self.damage_model=damage_model
		self.config=config
		self.status=0
		self.name=config["name"]
		self.attributes=config["attributes"]
		self.effects_damaged=config["effects_damaged"]
		self.effects_destroyed=config["effects_destroyed"]
		self.health=config["health"]
		self.maxhealth=self.health
		self.threshold=config["threshold_damaged"]
		self.regen_const=config["regen"]
		self.image_damaged=damage_model.root.gamedb.get_asset(dget(config, "image_damaged", "$BLANK"))
		self.image_destroyed=damage_model.root.gamedb.get_asset(dget(config, "image_destroyed", "$BLANK"))
		self.update_olds()

	def update_olds(self):
		self.olds={}
		for i in self.attributes:
			self.olds[i]=eval("self.damage_model.ship."+i)
		self.reset()
		self.deal_damage(0)

	def deal_damage(self, damage):
		self.health-=damage
		if self.health<=1 and self.status!=2:
			if not self.damage_model.ship.use_ai:
				self.damage_model.root.igconsole.post("Your "+self.name+" are now DESTROYED", (0,0,0), (255,0,0), bold=True)
			self.reset()
			self.do_destroyed()
			if self.health<=0:
				self.health=0
		elif self.health<self.threshold and self.health>1 and self.status!=1:
			if not self.damage_model.ship.use_ai:
				self.damage_model.root.igconsole.post("Your "+self.name+" are now DAMAGED", (0,0,0), (255,127,0), bold=True)
			self.reset()
			self.do_damaged()
		elif self.status!=0 and self.health>self.threshold:
			if not self.damage_model.ship.use_ai:
				self.damage_model.root.igconsole.post("Your "+self.name+" are now REPAIRED", (0,0,0), (0,255,0), bold=True)
			self.reset()
		if self.health<=0:
			self.health=0
		if self.health>=self.maxhealth:
			self.health=self.maxhealth

	def do_damaged(self):
		sg_postevent(UE_SYSTEM_DAMAGED, system=self, manager=self.damage_model)
		for i in self.attributes:
			exec "self.damage_model.ship."+i+"="+str(self.olds[i]*self.effects_damaged[self.attributes.index(i)])
		self.status=1

	def do_destroyed(self):
		sg_postevent(UE_SYSTEM_DESTROYED, system=self, manager=self.damage_model)
		for i in self.attributes:
			exec "self.damage_model.ship."+i+"="+str(self.olds[i]*self.effects_destroyed[self.attributes.index(i)])
		self.status=2

	def reset(self):
		sg_postevent(UE_SYSTEM_REPAIRED, system=self, manager=self.damage_model)
		for i in self.attributes:
			exec "self.damage_model.ship."+i+"="+str(self.olds[i])
		self.status=0

	def get_descriptor(self):
		return (self.name+":"+system_status[self.status][0]+" ["+str(int(self.health))+"]",system_status[self.status][1])

	def regen(self):
		self.deal_damage(-self.regen_const/self.damage_model.ship.root.fps)

	def save_to_config_node(self):
		return {
			"hp":self.health
		}

def _load_system(s, node):
	print "dealing "+str(s.health-node["hp"])+" damage to "+s.name
	s.deal_damage(s.health-node["hp"])
	return s

class DamageModel:
	def __init__(self, ship, hull=1, shields=0):
		self.hull=hull
		self.maxhull=hull
		self.shields=shields
		self.maxshields=shields
		self.ship=ship
		self.systems=[]
		self.root=self.ship.root

	def damage_hull(self, hull, precise_x=None, precise_y=None, source=None):
		if hull>0.1 and self.hull>0:
			px=self.ship.rotated_rect.centerx if precise_x==None else precise_x
			py=self.ship.rotated_rect.centery if precise_y==None else precise_y
			self.ship.particlemanager.add_particle(particles.make_hitNumber(self.root, "-"+str(int(hull)),
			 self.root.gamedb("font_standard_small"), px+random.randint(-30,30), py+random.randint(-30,30), (255,0,0)))
		self.hull-=hull
		sg_postevent(UE_HUL_DAMAGE_DEALT, system=self, amount=hull, x=precise_x, y=precise_y, source=source)
		if len(self.systems)>0:
			s=random.sample(self.systems,1)[0]
			if s:
				s.deal_damage(hull)
		if self.hull<=0:
			self.hull=0
			sg_postevent(UE_SHIP_DESTROYED, system=self, x=precise_x, y=precise_y, source=source)

	def damage_shields(self, shields, precise_x=None, precise_y=None, source=None):
		if shields>0.1 and self.shields>0:
			px=self.ship.rotated_rect.centerx if precise_x==None else precise_x
			py=self.ship.rotated_rect.centery if precise_y==None else precise_y
			self.ship.particlemanager.add_particle(particles.make_hitNumber(self.root, "-"+str(int(shields)),
			 self.root.gamedb("font_standard_small"), px+random.randint(-30,30), py+random.randint(-30,30), (0,0,255)))
		self.shields-=shields
		sg_postevent(UE_SHL_DAMAGE_DEALT, system=self, amount=shields, x=precise_x, y=precise_y, source=source)
		if self.shields<=0:
			self.damage_hull(abs(self.shields)*0.8)
			self.shields=0
			sg_postevent(UE_SHIELDS_DOWN, system=self, x=px, y=py, source=source)

	def damage(self, damage, peirce=0, px=None, py=None, source=None):
		self.damage_shields(damage*(1-peirce), px, py, source)
		self.damage_hull(damage*peirce, px, py, source)
		self.last_source=source
		sg_postevent(UE_DAMAGE_DEALT, system=self, amount=damage, peirce=peirce, x=px, y=py, source=source)

	def load_systems(self, config):
		"""Takes a list of dicts describing systems and adds them to its internal register.
		config - Loaded from JSON"""
		for i in config:
			self.systems.append(DamageSystem(self, i)) #Instanciate a DamageSystem
			self.systems.append(None) #Add a placeholder so there is only a 1/2 chance of damage going to a system

	def render_systems_full(self, screen, font, x=0, y=0):
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

	def render_infobox(self, screen, font, x, y, show_distance):
		"""Render a small view of the ship, its shields, hull, and energy
		screen - surface to render on
		font - font to use
		x, y - offset of top left corner of minimap BOX, not whole widget"""
		
		targetdistancex = abs(self.ship.rotated_rect.centerx - self.ship.root.state_manager.states["game"].player.rotated_rect.centerx)
		targetdistancey = abs(self.ship.rotated_rect.centery - self.ship.root.state_manager.states["game"].player.rotated_rect.centery)
		targetdistance = math.sqrt(targetdistancex**2 + targetdistancey**2)
		
		rotated_image, rotated_rect=rot_center(aspect_scale(self.ship.image, (50,50)), pygame.Rect((x+50-(self.ship.image.get_width()/2),y+50-(self.ship.image.get_height()/2)), self.ship.image.get_size()), self.ship.rigidbody.get_angle())
		screen.blit(rotated_image, (rotated_rect.x,rotated_rect.y))
		pygame.draw.rect(screen, (255,255,255), pygame.Rect(x,y,100,100), 4)
		pygame.draw.rect(screen, (255,0,0), pygame.Rect(x,y+100,(self.hull/self.maxhull)*100,20))
		r=font.render("HUL:"+str(int(self.hull))+"/"+str(int(self.maxhull)), False, (100,255,255))
		screen.blit(r, (x+50-(r.get_width()/2),y+100+10-(r.get_height()/2)))
		if self.maxshields>0:
			pygame.draw.rect(screen, (0,0,255), pygame.Rect(x,y-20,(self.shields/self.maxshields)*100,20))
			r=font.render("SHL:"+str(int(self.shields))+"/"+str(int(self.maxshields)), False, (0,175,175))
			screen.blit(r, (x+50-(r.get_width()/2),y-20+(r.get_height()/2)))
		pygame.draw.rect(screen, (0,255,0), pygame.Rect(x,y+120,(self.ship.current_power/self.ship.reactor_max)*100,20))
		r=font.render("PWR:"+str(int(self.ship.current_power))+"/"+str(int(self.ship.reactor_max)), False, (0,175,175))
		screen.blit(r, (x+50-(r.get_width()/2),y+120+10-(r.get_height()/2)))
		if show_distance==1:
			r=font.render("Target Distance:"+str(int(targetdistance)),False, (255,255,255))
			screen.blit(r, (x+50-(r.get_width()/2),y-40+(r.get_height()/2)))
		#Render subsystem icons
		ox=0
		for i in self.systems:
			if i:
				if i.status==1:
					screen.blit(i.image_damaged, (x+ox, y+140))
					ox+=16
				if i.status==2:
					screen.blit(i.image_destroyed, (x+ox, y+140))
					ox+=16

	def regen(self):
		if self.shields<self.maxshields:
			if self.ship.current_power>self.ship.config["shield_regen"]:
				self.shields+=self.ship.config["shield_regen"]/self.root.fps
				self.ship.current_power-=self.ship.config["shield_regen"]/self.root.fps
		if self.ship.current_power<self.ship.reactor_max:
			self.ship.current_power+=self.ship.reactor_regen*(1/self.root.fps)
		for system in self.systems:
			if system:
				system.regen()

	def dead(self):
		return self.hull==0

	def __call__(self, *args, **kwargs):
		self.damage(*args, **kwargs)

	def damage_system(self, damage, search_name=None, search_key=None):
		i=self.search_system(search_name, search_key)
		if i:
			i.deal_damage(damage)

	def search_system(self, search_name=None, search_key=None):
		if search_name:
			for i in self.systems:
				if i:
					if search_name.upper() in i.name.upper():
						return i
		elif search_key:
			for i in self.systems:
				if i:
					for e in i.attributes:
						if search_key.upper() in e.upper():
							return i

	def rebuild_systems(self):
		for i in self.systems:
			if i:
				i.update_olds()

	def save_systems_json(self):
		r=[]
		for i in self.systems:
			if i:
				r.append(i.save_to_config_node())
		return r

	def load_systems_json(self, node):
		c=0
		for n in node:
			if self.systems[c]:
				_load_system(self.systems[c], n)
			c+=1