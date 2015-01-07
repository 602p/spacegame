import pygame, rarity, assets, datetime, os, json, primitives, serialize, ai
from rotutil import *
from jsonutil import dget
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json

def init(root):
	if not 'item_factories' in dir(root):
		root.item_factories={}

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i)

def load_file(root, fname):
	debug("Load item_file '"+fname)
	with open(fname, 'r') as f:
		load_string(root, f.read())

def load_string(root, string):
	register_item(root, get_expanded_json(root.gamedb, json.loads(string)))

def register_item(root, config):
	root.item_factories[config["id"]]=create_item_factory(root, config)

def create_item_factory(root, config):
	return ItemFactory(root, config)

def create_item(root, name, parent, equipped=-1):
	return root.item_factories[name](parent, equipped)

def _deserialize_item(root, node, parent):
	item=create_item(root, node["id"], parent, node["equipped"])
	if item.equipped>-1:
		item.equip_actions()
	parent.inventory.append(item)

class ItemFactory:
	def __init__(self, root, json_dict):
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
		self.config=json_dict

		debug("Loaded item '"+self.id)

	def __call__(self, parent, equipped=-1):
		return Item(self.root, self.id, self.name, self.cost, self.mass, self.inventory_image, self.equipped_image,
			self.fire_required, self.hardpoint, self.rarity, self.passive_equip,
			self.passive_dequip, self.fire_events, equipped, parent, self.config)


class Item(serialize.SerializableObject):
	def __init__(self, root, id_str, name, cost, mass, inventory_image, equipped_image, fire_required,
		hardpoint, rarity, passive_equip, passive_dequip, fire_events, equipped, parent, config):
		self.cost=cost
		self.name=name
		self.root=root
		self.id_str=id_str
		self.inventory_image=inventory_image.copy() #Make a copy so we dont contaminate the gdb
		self.mass=mass
		self.hardpoint=hardpoint
		self.passive_equip=passive_equip
		self.passive_dequip=passive_dequip
		self.fire_events=fire_events
		self.equipped_image=equipped_image.copy() #Make a copy so we dont contaminate the gdb
		self.rarity=rarity
		self.fire_required=fire_required
		self.parent=parent
		self._config=config

		self.count=config.get("count", 1)

		self.ai_hints=[]

		if "ai_hints" in config:
			for i in config["ai_hints"]:
				if ai.has_ai_hint(self.root, i["name"]):
					self.ai_hints.append(ai.get_ai_hint(self.root, i["name"])(self, i))

		self.equipped=equipped

		self.last_fired=0

	def render_equipped(self, surface, scale=1):
		surface.blit(pygame.transform.scale(self.equipped_image, (
			self.equipped_image.get_width()*scale,
			self.equipped_image.get_height()*scale
			)), (0,0))
		#print "re"

	def render_inventory(self, surface):
		surface.blit(self.inventory_image, (0,0))

	def equip_actions(self):
		primitives.do_group_for_item(self.root, self.passive_equip, self)

	def equip(self, slot):
		self.equipped=slot
		self.equip_actions()

	def dequip_actions(self):
		primitives.do_group_for_item(self.root, self.passive_dequip, self)

	def dequip(self):
		self.equipped=-1
		self.dequip_actions()

	def fire_actions(self):
		self.last_fired=self.root.game_time
		primitives.do_group_for_item(self.root, self.fire_events, self)

	def can_fire(self):
		for i in self.fire_required:
			if i=="energy":
				if self.parent.current_power<self.fire_required[i]:
					return False
			if i=="enemy_selected":
				if self.parent.targeted==None and self.fire_required[i]:
					return False
			if i=="cooldown":
				if self.root.game_time-self.last_fired<self.fire_required[i]:
					return False
			if i=="distance<":
				targetdistancex = abs(self.parent.rotated_rect.centerx - self.parent.targeted.rotated_rect.centerx)
				targetdistancey = abs(self.parent.rotated_rect.centery - self.parent.targeted.rotated_rect.centery)
				targetdistance = math.sqrt(targetdistancex**2 + targetdistancey**2)
				if self.fire_required[i]<targetdistance:
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