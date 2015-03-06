from __future__ import division
import pygame, rarity, assets, datetime, os, json, primitives, serialize, ai, tooltips, absroot, textwrap
from rotutil import *
from jsonutil import dget
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json
from triggers import *
import entitybase
import logging
module_logger=logging.getLogger("sg.item")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	if not 'item_factories' in dir(root):
		root.item_factories={}
	serialize.register_load_mode(root, "item", _deserialize_item)

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

def create_item(root, name, parent, equipped=-1, count=None):
	i=root.item_factories[name](parent, equipped)
	if count:
		i.count=count
	return i

def _deserialize_item(root, node, parent):
	item=create_item(root, node["id"], parent, node["equipped"])
	item.count=node["count"]
	if item.equipped>-1:
		item.equip_actions()
	parent.inventory.append(item)
	item.do_additional_load(node)
	return item

class ItemFactory:
	def __init__(self, root, json_dict):
		# self.cost=json_dict["cost"]
		# self.id=json_dict["id"]
		# self.name=json_dict["name"]
		# self.inventory_image=root.gamedb.get_asset(json_dict["inventory_image"])
		# self.equipped_image=root.gamedb.get_asset(json_dict["equipped_image"])
		# self.mass=json_dict["mass"]
		# self.hardpoint=json_dict["mount_type"]
		# self.rarity=rarity.Rarity(json_dict["rarity"])
		# self.fire_required=json_dict["required"]
		# self.passive_equip=json_dict["equip"]
		# self.passive_dequip=json_dict["dequip"]
		# self.fire_events=json_dict["fire_events"]
		self.root=root
		self.config=json_dict

		debug("Cached item '"+self.config["id"])

	def __call__(self, parent, equipped=-1):
		return Item(self.root, equipped, parent, self.config)


class Item(serialize.SerializableObject, entitybase.Triggerable, entitybase.TiggerablePosteventAdapterMixin, tooltips.GenericTooltipMixin):
	def __init__(self, root, equipped, parent, json_dict):
		config=json_dict
		# self.costper=cost
		# self.name=name
		# self.root=root
		# self.id_str=id_str
		# self.inventory_image=inventory_image.copy() #Make a copy so we dont contaminate the gdb
		# self.mass=mass
		# self.hardpoint=hardpoint
		# self.passive_equip=passive_equip
		# self.passive_dequip=passive_dequip
		# self.fire_events=fire_events
		# self.equipped_image=equipped_image.copy() #Make a copy so we dont contaminate the gdb
		# self.rarity=rarity.Rarity(config["rarity"])
		self.triggers={}
		self.costper=json_dict.get("cost", 0)
		self.id_str=json_dict["id"]
		self.name=json_dict["name"]
		self.inventory_image=root.gamedb.get_asset(json_dict["inventory_image"]).copy()
		self.equipped_image=root.gamedb.get_asset(json_dict["equipped_image"]).copy()
		self.mass=json_dict["mass"]
		self.hardpoint=json_dict["mount_type"]
		self.rarity=rarity.Rarity(json_dict["rarity"])
		self.fire_required=json_dict["required"]
		self.passive_equip=json_dict["equip"]
		self.passive_dequip=json_dict["dequip"]
		self.fire_events=json_dict["fire_events"]
		self.tags=json_dict.get("tags", [])
		self.tags.append("_all")
		self.can_sell=json_dict.get("can_sell", True)
		self.can_buy=json_dict.get("can_buy", True)
		self.root=root

		self.parent=parent
		self._config=json_dict
		self.config=json_dict

		self.count=config.get("count", 1)


		self.ai_hints=[]

		if "ai_hints" in config:
			for i in config["ai_hints"]:
				if ai.has_ai_hint(self.root, i["name"]):
					self.ai_hints.append(ai.get_ai_hint(self.root, i["name"])(self, i))

		self.equipped=equipped

		self.last_fired=0
		#self.get_rotated_image()

	def reparent(self, parent):
		self.parent=parent
		self.equipped=-1

	def get_rotated_image(self, scale=1):
		#if "ammo" in self.id_str:print "gri"
		self.rotated_image, self.rotated_rect=rot_center(pygame.transform.scale(self.equipped_image, (
			self.equipped_image.get_width()*scale,
			self.equipped_image.get_height()*scale)),
		 pygame.Rect(self.get_center(), self.equipped_image.get_size()), self.parent.rigidbody.get_angle())

	def render_equipped(self, surface, hardpoint, scale=1):

		if self.equipped!=-1:
			if "ammo" in self.id_str:print "rq"
			self.get_rotated_image(scale)
			surface.blit(self.rotated_image, pygame.Rect(self.get_center(), self.rotated_rect.size))
		# surface.draw_rect((255,0,0), pygame.Rect(self.get_center(),(2,2)))
		# surface.draw_rect((0,0,255), self.rotated_rect, 1)

	def get_desc_text(self):
		d = [str(self.count)+"x : "+self.name]
		if self.equipped!=-1:
			d.append("Equipped in slot  "+str(self.equipped))
		else:
			d.append("Not equipped")
		d.append(self.config.get("desc_text", "(No Description Availible)"))
		return d

	def get_inventory_image(self):
		surface=pygame.Surface((64,64)).convert_alpha()
		surface.fill((0,0,0,0))
		surface.blit(self.inventory_image, (0,0))
		font=self.root.gamedb("font_sys_mono")
		font.set_bold(1)
		surface.blit(font.render(str(self.count), 0, (0,0,255)), (0,0))
		#print "a"
		if "item" in self.fire_required.keys() and not self.config.get("hide_ammo", False):
			#print "b"
			none=1
			for item in self.parent.inventory:
				#print "c"
				if item.id_str==self.fire_required["item"]:
					none=0
					#print "r"
					surface.blit(font.render("("+str(item.count)+")", 0, (0,255,0)), (20,0))
			if none:
				surface.blit(font.render("(0)", 0, (255,0,0)), (20,0))
		font.set_bold(0)
		return surface

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
			if i=="item":
				g=1
				for item in self.parent.inventory:
					if item.id_str==self.fire_required[i]:
						g=0
				if g: return False
		self.parent.current_power-=dget(self.fire_required,"energy",0)
		return True

	def fire(self):
		if self.can_fire():
			#print "canfire"
			self.sg_postevent(UE_FIRE_REQUIRE_SUCCESS, item=self)
			#self.trigger(UE_FIRE_REQUIRE_SUCCESS)
			self.sg_postevent(UE_BEFORE_FIRE, item=self)
			#self.trigger(UE_BEFORE_FIRE)
			self.fire_actions()
			self.sg_postevent(UE_AFTER_FIRE, item=self)
			if "item" in self.fire_required.keys():
				for item in self.parent.inventory:
					if item.id_str==self.fire_required["item"]:
						item.consume_one()
				# if self.id_str==self.fire_required["item"]:
				# 	self.consume_one()
		else:
			self.sg_postevent(UE_FIRE_REQUIRE_FAIL, item=self)
			
	def save_to_config_node(self):
		return {
			"__deserialize_handler__":"item",
			"id":self.id_str, 
			"equipped":self.equipped, 
			"count":self.count
		}

	def load_from_config_node(self, node):
		self.count=node["count"]

	def get_center_(self):
		if self.equipped>-1:
			#if "ammo" in self.id_str:print "return(equp)"
			#if "ammo" in self.id_str:print "DOING THING"
			return rotate_point(self.parent.rotated_rect.center, [self.parent.rigidbody.x+self.parent.hardpoints[self.equipped]["x"],
			 self.parent.rigidbody.y+self.parent.hardpoints[self.equipped]["y"]], -self.parent.rigidbody.get_angle())
			#if "ammo" in self.id_str:print "DONE THING"
		else:
			#if "ammo" in self.id_str:print "return(else)"
			return rotate_point(self.parent.rotated_rect.center, [self.parent.rigidbody.x,
			 self.parent.rigidbody.y], -self.parent.rigidbody.get_angle())

	def get_center(self):
		#if "ammo" in self.id_str:print "get_center"
		if "rotated_rect" not in self.__dict__.keys(): self.rotated_rect=pygame.Rect(0,0,0,0)
		return (self.get_center_()[0]-self.rotated_rect.width/2,self.get_center_()[1]-self.rotated_rect.height/2)

	def consume_one(self):
		self.consume(1)

	def consume(self, amount):
		self.count-=amount
		#debug("Consuming one "+self.id_str)
		if self.count<1:
			#debug("Consumed all. Deleting")
			self.dequip()
			del self.parent.inventory[self.parent.inventory.index(self)]

	def get_cost_all(self):
		return self.cost*self.count

	def get_cost_one(self):
		return self.cost

	def get_insert_dict(self):
		return {
			"name":self.name
		}

	def update(self, dt):
		pass

	def do_additional_load(self, config):
		pass

	def get_mass(self):
		return self.count*self.mass

	def get_cost(self):
		return self.count*self.costper

	def tt_render_image(self):
		self.tt_image_init((1000,1000))
		self.tt_image.blit(self.inventory_image, (0,0))
		self.tt_image.blit(absroot.gamedb("font_item_title").render(self.name, 1, (20,20,20)), (70,0))
		text=self.config.get("desc_text", "Some indescribably horror.")
		image_1=tooltips.render_wrapped_text(text, 400, absroot.gamedb("font_item_desc"), (40,40,40))
		self.tt_image.blit(
			image_1,
			(70,absroot.gamedb("font_item_title").size("|")[1]))
		absroot.gamedb("font_item_desc").set_italic(1)
		text=""
		for i in self.fire_required:
			if i=='enemy_selected':
				if self.fire_required[i]:
					text+="\nRequires targeted enemy."
			if i=="energy":
				text+="\nRequires "+str(self.fire_required[i])+" energy."
			if i=="cooldown":
				text+="\nRequires "+str(self.fire_required[i])+" seconds between shots."
			if i=="item":
				text+="\nRequires a "+str(self.fire_required[i])+" to fire."
			if i=="distance<":
				text+="\nTarget must be closer than "+str(self.fire_required[i])+"u."
		self.tt_image.blit(
			tooltips.render_wrapped_text(text, 400, absroot.gamedb("font_item_desc"), (40,40,40)),
			(70,absroot.gamedb("font_item_title").size("|")[1]+image_1.get_height()+10))
		absroot.gamedb("font_item_desc").set_italic(0)
		absroot.gamedb("font_item_desc").set_bold(1)

		self.tt_image.blit(
			absroot.gamedb("font_item_desc").render("Mass: "+str(self.get_mass()), 1 ,(40,40,40))
			,(0,65))
		self.tt_image.blit(
			absroot.gamedb("font_item_desc").render("Cost: "+str(self.get_cost()), 1 ,(40,40,40))
			,(0,65+absroot.gamedb("font_item_desc").size("|")[1]))

		absroot.gamedb("font_item_desc").set_bold(0)
		self.tt_image_clip()
		self.tt_add_box()

	tt_last_rerender_count=0
	def tt_needs_rerender(self):
		if self.tt_last_rerender_count!=self.count:
			self.tt_last_rerender_count=self.count
			return True
		return False
