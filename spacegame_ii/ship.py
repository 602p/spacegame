from __future__ import division
import rarity, os, json, serialize, item, assets, random, assets, pygame, math, particles, physics, damage, pygame, primitives
from math import cos, sin, radians, degrees
from rotutil import *
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json, dget

def init(root):
	if not 'ship_factories' in dir(root):
		root.ship_factories={}

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i, dname)

def load_file(root, fname, package_root):
	debug("Load ship_file '"+fname+"' from '"+package_root+"'")
	with open(fname, 'r') as f:
		load_string(root, f.read(), package_root)

def load_string(root, string, package_root):
	register_ship(root, get_expanded_json(root.gamedb, json.loads(string)), package_root)

def register_ship(root, config, package_root):
	root.ship_factories[config["id"]]=create_ship_factory(root, config, package_root)

def create_ship_factory(root, config, package_root):
	return ShipFactory(root, package_root, config)

def create_ship(root, id_, x=0, y=0, with_equip=1):
	return root.ship_factories[id_](x, y, with_equip)

class ShipFactory:
	def __init__(self, root, package_root, config):
		self.root=root

		self.image=root.gamedb.get_asset(config["image"])
		self.mask=pygame.mask.from_surface(self.image)
		self.id_string=config["id"]
		self.name=config["name"]
		self.hull=config["hull"]
		self.mass=config["mass"]
		self.cost=config["cost"]
		self.cargo=config["cargo"]
		self.start_speed=config["start_speed"]
		self.reactor_max=config["reactor_max"]
		self.reactor_regen=config["reactor_regen"]
		self.hardpoints=config["hardpoints"]
		self.start_equip=config["start_equip"]
		self.engine_sources=config["engine_sources"]
		self.shields=config["shields"]
		self.rarity=rarity.Rarity(config["rarity"])
		self.max_speed=config["max_speed"]
		self.turn_rate=config["turn_rate"]
		self.systems=config["systems"]
		self.config=config

		debug("Loaded ship '"+self.id_string)

	def __call__(self, x=0, y=0, with_equip=1):
		s = Ship(self.root, self.image, self.id_string, self.name, self.hull, self.mass, self.cost, self.cargo,\
			self.start_speed, self.reactor_max, self.reactor_regen, self.hardpoints, self.engine_sources, self.shields,
			self.rarity, self.max_speed, self.turn_rate, self.systems, self.config, x, y)
		if with_equip:
			for i in self.start_equip:
				s.inventory.append(item.create_item(self.root, i["item_name"], s, i["equipped"]))
		return s

class Ship(serialize.SerializableObject):
	def __init__(self, root, image, id_string, name, hull, mass, cost, cargo, start_speed, reactor_max,
		reactor_regen, hardpoints, engine_sources, shields, rarity, max_speed, turn_rate, systems, config, x, y):
		self.root=root

		self.image=image.copy() #Make a copy so we dont contaminate the gdb
		self.id_string=id_string
		self.name=name
		self.mass=mass
		self.cost=cost
		self.cargo=cargo
		self.speed=start_speed
		self.reactor_max=reactor_max
		self.reactor_regen=reactor_regen
		self.current_power=reactor_max
		self.hardpoints=hardpoints
		self.engine_sources=engine_sources
		self.rarity=rarity
		self.currshields=shields
		self.max_speed=max_speed
		self.turn_rate=turn_rate

		self._config=config

		self.damage=damage.DamageModel(self, hull, shields)
		self.damage.load_systems(systems)

		self.inventory=[]
		self.rigidbody=physics.RigidBody2D(mass, x, y, None)

		self.particlemanager=particles.ParticleManager()

		self.kill=False

		self.can_be_hit=True

	def get_inventory_mass(self):
		m=0
		for i in self.inventory:
			m+=i.mass
		return m

	def get_mass(self):
		return self.get_inventory_mass()+self.mass

	def pick_up(self, item):
		if self.get_inventory_mass()+item.mass<self.cargo:
			self.inventory.append(item)
			return True
		else:
			return False

	def get_item_in_hardpoint(self, id_int):
		for i in self.inventory:
			if i.equipped==id_int:
				return i
		return None

	def equip_item_to_hardpoint(self, item, id_int):
		if self.get_item_in_hardpoint(id_int)==None:
			item.equip(id_int)

	def deqip_item_from_hardpoint(self, id_int):
		item.deqip()

	def fire_item_in_hardpoint(self, id_int):
		if self.get_item_in_hardpoint(id_int)!=None:
			self.get_item_in_hardpoint(id_int).fire()

	def save_to_config_node(self):
		inv=[]
		for item in self.inventory:
			inv.append(item.save_to_config_node())
		return {"__deserialize_handler__":"ship", "ship_id":self.id_string, "inventory":inv, "current_hull":self.currhull,
		"current_shields":self.currshields}

	def tick(self, screen, time):
		self.rotated_image, self.rotated_rect=rot_center(self.image.copy(), pygame.Rect((self.rigidbody.x, self.rigidbody.y), self.image.get_size()), self.rigidbody.get_angle())
		self.rotated_mask=pygame.mask.from_surface(self.rotated_image)
		screen.blit(self.rotated_image, (self.rotated_rect.x,self.rotated_rect.y))
		self.render_engines()
		self.render_items()
		self.particlemanager.update()
		self.particlemanager.draw(self.root.screen)

		if self.rigidbody.get_magnitude()<0:
			self.rigidbody.set_magnitude(0)
		if self.rigidbody.get_magnitude()>self.max_speed:
			self.rigidbody.set_magnitude(self.max_speed)
		
		self.rigidbody.update_in_seconds(time)
		self.rigidbody.mass=self.get_mass()

		if self.damage.dead(): self.kill=True

		self.damage.regen()

		if self.damage.dead(): self.die()

	def render_items(self):
		for i in self.inventory:
			if i.equipped!=-1:
				i.render_equipped(self.image.subsurface(pygame.Rect(( self.hardpoints[i.equipped]["x"]-(i.equipped_image.get_width()/2) ,
				  self.hardpoints[i.equipped]["y"]-(i.equipped_image.get_height()/2) ), i.equipped_image.get_size() ) ) )

	def render_engines(self):
		if self.rigidbody.moving()>0:
			for emitter in self.engine_sources:
				c=0
				while c!=emitter["density"]+1:
					y_=self.rigidbody.y+emitter["y"]+random.randint(0,1)-random.randint(0,2)
					x_=self.rigidbody.x+emitter["x"]+random.randint(0,emitter["width"])-random.randint(0,emitter["width"]*2)
					color=emitter["color"]
					point=rotate_point(self.rotated_rect.center, [x_, y_], -self.rigidbody.get_angle())
					self.particlemanager.add_particle(particles.make_floater(self.root, point[0], point[1], color))
					c+=1

	def exert_engine(self):
		self.rigidbody.exert_in_vector(self.speed)
		
	def exert_reverse_engine(self):
		self.rigidbody.exert_in_vector(-self.speed*4)

	def die(self):
		for i in dget(self._config, "ship_die", []):
			if not primitives.run_primitive(self.root, i["primitive"], i, self): break