import pygame, rarity, assets, datetime, os, json, primitives, serialize
from rotutil import *
from jsonutil import dget
from logging import debug, info, warning, error, critical

def init(root):
	if not 'item_factories' in dir(root):
		root.item_factories={}

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i, dname)

def load_file(root, fname, package_root):
	debug("Load item_file '"+fname+"' from '"+package_root+"'")
	with open(fname, 'r') as f:
		load_string(root, f.read(), package_root)

def load_string(root, string, package_root):
	register_item(root, json.loads(string), package_root)

def register_item(root, config, package_root):
	root.item_factories[config["id"]]=create_item_factory(root, config, package_root)

def create_item_factory(root, config, package_root):
	return ItemFactory(root, package_root, config)

def create_item(root, name, parent, equipped=-1):
	return root.item_factories[name](parent, equipped)

def _deserialize_item(root, node, parent):
	item=create_item(root, node["id"], parent, node["equipped"])
	if item.equipped>-1:
		item.equip_actions()
	parent.inventory.append(item)

class ItemFactory:
	def __init__(self, root, package_root, json_dict):
		self.cost=json_dict["cost"]
		self.id=json_dict["id"]
		self.name=json_dict["name"]
		self.inventory_image=root.gamedb.get_asset(json_dict["inventory_image"])
		self.equipped_image=root.gamedb.get_asset(json_dict["equipped_image"])
		self.mass=json_dict["mass"]
		self.hardpoint=json_dict["mount_type"]
		self.rarity=rarity.Rarity(json_dict["rarity"])
		self.fire_required=json_dict["required"]
		self.passive_equip=json_dict["equip"]
		self.passive_dequip=json_dict["dequip"]
		self.fire_events=json_dict["fire_events"]
		self.root=root

		debug("Loaded item '"+self.id)

	def __call__(self, parent, equipped=-1):
		return Item(self.root, self.id, self.name, self.cost, self.mass, self.inventory_image, self.equipped_image,
			self.fire_required, self.hardpoint, self.rarity, self.passive_equip,
			self.passive_dequip, self.fire_events, equipped, parent)


class Item(serialize.SerializableObject):
	def __init__(self, root, id_str, name, cost, mass, inventory_image, equipped_image, fire_required,
		hardpoint, rarity, passive_equip, passive_dequip, fire_events, equipped, parent):
		self.cost=cost
		self.name=name
		self.root=root
		self.id_str=id_str
		self.inventory_image=inventory_image
		self.mass=mass
		self.hardpoint=hardpoint
		self.passive_equip=passive_equip
		self.passive_dequip=passive_dequip
		self.fire_events=fire_events
		self.equipped_image=equipped_image
		self.rarity=rarity
		self.fire_required=fire_required
		self.parent=parent

		self.equipped=equipped

		self.last_fired=0

	def render_equipped(self, surface):
		surface.blit(self.equipped_image, (0,0))

	def render_inventory(self, surface):
		surface.blit(self.inventory_image, (0,0))

	def equip_actions(self):
		for i in self.passive_equip:
			if not primitives.run_primitive(self.root, i["primitive"], i, self): break #if the primitive returns false, don't call rest

	def equip(self, slot):
		self.equipped=slot
		self.equip_actions()

	def dequip_actions(self):
		for i in self.passive_dequip:
			if not primitives.run_primitive(self.root, i["primitive"], i, self): break

	def dequip(self):
		self.equipped=-1
		self.dequip_actions()

	def fire_actions(self):
		self.last_fired=self.root.game_time
		for i in self.fire_events:
			if not primitives.run_primitive(self.root, i["primitive"], i, self): break

	def can_fire(self):
		for i in self.fire_required:
			if i=="energy":
				if self.parent.current_power<self.fire_required[i]:
					return False
			if i=="enemy_selected":
				if self.parent.targeted==None:
					return False
			if i=="cooldown":
				if self.root.game_time-self.last_fired<self.fire_required[i]:
					return False
		self.parent.current_power-=dget(self.fire_required,"energy",0)
		return True

	def fire(self):
		if self.can_fire():
			self.fire_actions()
	
	def save_to_config_node(self):
		return {"__deserialize_handler__":"item", "id":self.id_str, "equipped":self.equipped}

	def get_center(self):
		if self.equipped>-1:
			return rotate_point(self.parent.rotated_rect.center, [self.parent.rigidbody.x+self.parent.hardpoints[self.equipped]["x"],
			 self.parent.rigidbody.y+self.parent.hardpoints[self.equipped]["y"]], -self.parent.rigidbody.get_angle())