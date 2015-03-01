from __future__ import division
import rarity, os, json, serialize, item, assets, entitybase, faction
import random, assets, pygame, math, particles, physics, damage, pygame, primitives, ai
from triggers import *
from math import cos, sin, radians, degrees
from rotutil import *
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json, dget
import logging
module_logger=logging.getLogger("sg.ship")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	if not 'ship_factories' in dir(root):
		root.ship_factories={}
	serialize.register_load_mode(root, "ship", _load_ship)

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i)

def load_file(root, fname):
	debug("Load ship_file '"+fname)
	with open(fname, 'r') as f:
		load_string(root, f.read(), path=fname)

def load_string(root, string, path=None):
	json_o=get_expanded_json(root.gamedb, json.loads(string))
	register_ship(root, json_o)
	root.gamedb.assets["ship:"+json_o["id"]]=json_o
	root.gamedb.metadata["ship:"+json_o["id"]]={"path":path, "node":json_o, "is_ship":False}

def register_ship(root, config):
	root.ship_factories[config["id"]]=create_ship_factory(root, config)
	#

def create_ship_factory(root, config):
	return ShipFactory(root, config)
	#

def create_ship(root, id_, x=0, y=0, with_equip=1, ai=True):
	debug("Instantiating ship "+str(id_)+" at "+str((x,y,)) + ". w_e: "+str(with_equip)+". u_a: "+str(ai))
	return root.ship_factories[id_](x, y, with_equip, ai)

def _load_ship(root, node, parent):
	#print ">>>"+str(node)
	s = create_ship(root, node["ship_id"], 0, 0, not "packed" in node.keys(), node.get("ai", 1))
	
	if "packed" in node.keys():
		for item in node["inventory"]:
			serialize.load_from_node(root, item, s)
		s.damage.hull=node["currhull"]
		s.damage.shields=node["currshld"]
		s.current_power=node["currpwr"]
		s.damage.load_systems_json(node["damagesystems"])
		s.rigidbody   = physics._load_rigidbody(node["rigidbody"], s)
		s.hash_id=node["hash_id"]
		s.triggers.update(node["triggers"])
		if node.get("ai",1):
			s.ai=ai._load_controller(root, s, node["ai_controller"])
		for item in node.get("factions", []):
			faction.get_faction(item).do_join(s, force_functional=1)
	else:
		s.rigidbody.x=node["x"]
		s.rigidbody.y=node["y"]
		for item in node.get("factions", []):
			faction.get_faction(item).do_join(s, force_functional=0)
	s.player_relations=node.get("relations", 0)
	

	return s

class ShipFactory:
	def __init__(self, root, config):
		self.root=root

		self.image=root.gamedb.get_asset(config["image"])
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

	def __call__(self, x=0, y=0, with_equip=1, ai=True):
		s = Ship(self.root, self.image, self.id_string, self.name, self.hull, self.mass, self.cost, self.cargo,\
			self.start_speed, self.reactor_max, self.reactor_regen, self.hardpoints, self.engine_sources, self.shields,
			self.rarity, self.max_speed, self.turn_rate, self.systems, self.config, x, y, use_ai=ai)
		if with_equip:
			for i in self.start_equip:
				s.inventory.append(item.create_item(self.root, i["item_name"], s, i["equipped"]))
		return s

class Ship(serialize.SerializableObject, entitybase.FlaggedEntity, entitybase.TiggerablePosteventAdapterMixin):
	can_be_targeted=1
	def __init__(self, root, image, id_string, name, hull, mass, cost, cargo, start_speed, reactor_max,
		reactor_regen, hardpoints, engine_sources, shields, rarity, max_speed, turn_rate, systems, config, x, y, use_ai=True):
		self.root=root

		self.image=image.copy() #Make a copy so we dont contaminate the gdb
		self.id_string=id_string
		self.id_str=id_string
		self.str_id=id_string
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

		self.config=config
		self.triggers=self.config.get("triggers",{})
		self.player_relations=self.config.get("relations", 0)

		self.damage=damage.DamageModel(self, hull, shields)
		self.damage.load_systems(systems)

		self.inventory=[]
		self.rigidbody=physics.RigidBody2D(mass, x, y, None)

		self.particlemanager=particles.ParticleManager()

		self.kill=False

		self.can_be_hit=True

		self.selected_wep=0

		self.targeted=None

		self.use_ai=use_ai
		if self.use_ai:
			self.ai=ai.AIController(self, config["ai"])

		self.render_items()
		self.rerotate()

		self.rotated_in_flight=0
		self.can_be_hit=config.get("can_be_hit", True)
		self.can_be_targeted=config.get("can_be_targeted", True)
		self.can_save=not config.get("disable_saving", False)

		self.hash_id=hash(self)

		self.faction_memberships=[]

	def get_faction_attr(self, key, default="[[A faction attribute could not be found, and a default was not provided]]"):
		debug("Seeking '"+key+"' in faction data")
		for i in self.faction_memberships:
			#print faction.get_faction(i).config.keys()
			if key in faction.get_faction(i).config.keys():
				return faction.get_faction(i).config[key]
		return default

	def get_inventory_mass(self):
		m=0
		for i in self.inventory:
			m+=i.mass
		return m

	def get_mass(self):
		return self.get_inventory_mass()+self.mass

	def pick_up(self, item):
		#self.triggermanager("on_pickup_attempt", item)
		if self.get_inventory_mass()+item.mass<self.cargo or 1:
			self.inventory.append(item)
			#self.triggermanager("on_pickup_success", item)
			return True
		else:
			#self.triggermanager("on_pickup_failure", item)
			return False

	def get_item_in_hardpoint(self, id_int):
		for i in self.inventory:
			if i.equipped==id_int:
				return i
		return None

	def try_stack(self, item):
		for iitem in self.inventory:
			if iitem!=item:
				if iitem.id_str==item.id_str:
					iitem.count+=item.count
					del self.inventory[self.inventory.index(item)]
					return

	def try_split(self, itemx, count):
		assert count<itemx.count, "Tried to take more than you have"
		itemx.count-=count
		self.inventory.append(item.create_item(self.root, itemx.id_str, self, -1, count))

	def find_hardpoint_for_item(self, item):
		for i in self.hardpoints:
			if self.get_item_in_hardpoint(self.hardpoints.index(i))==item:
				return self.hardpoints.index(i)
		return None

	def equip_item_to_hardpoint(self, item, id_int):
		#self.triggermanager("on_equip_attempt", item, id_int)
		if self.get_item_in_hardpoint(id_int)==None:
			item.equip(id_int)
			#self.triggermanager("on_equip_success", item, id_int)

	def deqip_item_from_hardpoint(self, id_int):
		item.deqip()
		#self.triggermanager("on_item_dequip", item)

	def fire_item_in_hardpoint(self, id_int):
		self.sg_postevent(UE_FIRE_ATTEMPT, ship=self, hardpoint=id_int)
		if self.get_item_in_hardpoint(id_int)!=None:
			self.sg_postevent(UE_FIRE_EQUIPPED, ship=self, hardpoint=id_int)
			self.get_item_in_hardpoint(id_int).fire()
		else:
			self.sg_postevent(UE_FIRE_UNEQUIPPED, ship=self, hardpoint=id_int)

	def rerotate(self):
		self.rotated_image, self.rotated_rect=rot_center(self.image, pygame.Rect((self.rigidbody.x, self.rigidbody.y), self.image.get_size()), self.rigidbody.get_angle())
		self.rotated_mask=pygame.mask.from_surface(self.rotated_image)

	def tick(self, screen, time, ovveride_norotate=False):
		
		#screen.draw_rect((0,0,255), self.rotated_rect)
		
		self.render_items(False)
		if self.config.get("render_rotation", True) or ovveride_norotate or self.rotated_in_flight==0:
			self.rerotate()
			self.rotated_in_flight=1
			#self.rotated_image, delete=rot_center(self.image, pygame.Rect((self.rigidbody.x, self.rigidbody.y), self.image.get_size()), self.rigidbody.get_angle())

		screen.blit(self.rotated_image, (self.rotated_rect.x,self.rotated_rect.y))
		self.render_items(True)
		self.render_engines()
		self.particlemanager.update()
		self.particlemanager.draw(self.root.screen)

		for i in self.inventory:
			i.update(time)

		if self.rigidbody.get_magnitude()<-self.max_speed/8:
			self.rigidbody.set_magnitude(-self.max_speed/8)
		if self.rigidbody.get_magnitude()>self.max_speed:
			self.rigidbody.set_magnitude(self.max_speed)
		
		self.rigidbody.update_in_seconds(time)
		self.rigidbody.mass=self.get_mass()

		if self.damage.dead():
			self.kill=True
			self.die()

		self.damage.regen()

		if self.use_ai:
			self.ai.update()

	def render_items(self, render_top=True):
		for i in self.inventory:
			if i.equipped!=-1:
				if render_top==self.hardpoints[i.equipped].get("render_on_top", True):
					i.render_equipped(self.root.screen, self.hardpoints[i.equipped], self.hardpoints[i.equipped].get("scale", 1))
				# scaledsize=(i.equipped_image.get_size()[0]*self.hardpoints[i.equipped].get("scale", 1), i.equipped_image.get_size()[0]*self.hardpoints[i.equipped].get("scale", 1))
				# i.render_equipped(self.image.subsurface(pygame.Rect(( self.hardpoints[i.equipped]["x"]-(scaledsize[0]/2) ,
				#   self.hardpoints[i.equipped]["y"]-(scaledsize[1]/2) ), scaledsize ) ), self.hardpoints[i.equipped].get("scale", 1) )

	def render_engines(self):
		if self.rigidbody.moving()>self.root.settings["graphics"]["min_trail_speed"]:
			for emitter in self.engine_sources:
				random.seed(self.root.game_time)					
				y_=self.rigidbody.y+emitter["y"]
				x_=self.rigidbody.x+emitter["x"]
				x_, y_=rotate_point(self.rotated_rect.center, [x_, y_], -self.rigidbody.get_angle())
				self.particlemanager.add_particles(particles.make_explosion_cfg(self.root, x_, y_, emitter["style"]))

	def exert_engine(self):
		self.rigidbody.exert_in_vector(self.speed)
		
	def exert_reverse_engine(self):
		self.rigidbody.exert_in_vector(-self.speed*4)

	def die(self):
		debug(self.name+" was destroyed")
		self.sg_postevent(UE_SHIP_DIE_RUN, ship=self)
		primitives.do_group_for_ship(self.root, dget(self.config, "ship_die", []), self)

	def save_to_config_node(self):
		inv=[]
		for item in self.inventory:
			inv.append(item.save_to_config_node())
		d = {
			"__deserialize_handler__":"ship", 
			"ship_id":self.id_string, 
			"inventory":inv, 
			"currhull":self.damage.hull,
			"currshld":self.damage.shields,
			"damagesystems":self.damage.save_systems_json(),
			"rigidbody":self.rigidbody.save_to_config_node(),
			"ai":self.use_ai,
			"currpwr":self.current_power,
			"packed":True,
			"hash_id":self.hash_id,
			"triggers":self.serialize_triggers(),
			"relations":self.player_relations,
			"factions":self.faction_memberships
		}
		if self.use_ai:
			d["ai_controller"]=self.ai.save_to_config_node()
		return d

	def __enter__(self, *a, **k):
		return self

	def __exit__(self, *a, **k):
		debug("Calling _finalize")
		try:
			self.root.savegame.database["packed_entities"][self._source_sector_id][self._source_idx]=self.save_to_config_node()
			debug("_finalize completed")
			print "_finalize run on get_entity_by_id::ship_ref"
		except AttributeError:
			pass

	def finalize(self):
		self.__exit__()