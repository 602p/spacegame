import json, jsonutil, absroot, primitives
from logging import debug, info, warn, error, critical
from triggers import *

def init(root):
	root.factions={}

def load_file(root, fn):
	debug("Loading faction_file: "+fn)
	with open(fn, 'r') as fd:
		jsone=jsonutil.get_expanded_json(root.gamedb, json.load(fd))
		root.factions[jsone["id"]] = Faction(jsone)

class Faction(object):
	#Name
	#Desc
	#Longname
	#Relations
	#Factions
	#Triggers
	#Attached ships
	#Inventory
	#Currency 
	def __init__(self, config):
		self.config=config
		self.id_str=config["id"]
		self.name=config.get("name", "UNS_name")
		self.longname=config.get("longname", "UNS_longname")
		self.description=config.get("description", "UNS_description")
		self.color=config.get("color", [255,255,255])
		self.tags=config.get("tags",[])
		self.join_required=config.get("join_requirements",[])
		self.leave_required=config.get("leave_requirements",[])
		self.join_effects=config.get("join_effects",[])
		self.leave_effects=config.get("leave_effects",[])
		self.relations=config.get("relations",{})

	def do_join(self, ship):
		primitives.do_group_for_ship(absroot, sef.join_effects, ship)
		sg_postevent

	def can_join(self, ship):
		return primitives.do_group_for_ship(absroot, sef.join_effects, ship)

	def try_join(self, ship):
		if self.can_join(ship):
			self.do_joins(ship)
			return True
		return False

class FactionManager(object):
	def __init__(self, root):
		self.root=root
		self.relations={}
		#\
		# \----> Lookuptable of FACTION_1,FACTION_2:RELATION (order of FACTION_1,FACTION_2 is alphabetical)

	def get_lookup_id(self, factions):
		return sorted(factions)[0]+","+sorted(factions)[1]

	def update_relations(self):
		for faction1 in self.root.factions.itervalues():
			for faction2 in self.root.factions.itervalues():
				if self.get_lookup_id([faction1.id_str, faction2.id_str]) not in self.relations:
					if faction1.relations.get(faction2.id_str, None)!=None or faction2.relations.get(faction1.id_str, None)!=None:
						self.relations[self.get_lookup_id([faction1.id_str, faction2.id_str])]=faction1.relations.get(faction2.id_str)+faction2.relations.get(faction1.id_str)

	def inc_relations(self, faction1, faction2, amount):
		self.relations[self.get_lookup_id([faction1.id_str, faction2.id_str])]+=amount

	def update_newgame(self):
		self.update_relations()

	def save_to_config_node(self):
		return {
			"relations":self.relations
		}

	@classmethod
	def load_from_config_node(cls, node):
		temp = cls(absroot)
		temp.relations=node["relations"]

# ------------|-FEDERATION-|-KLINGON_EMP-|-VULCAN_CMD-|
# FEDERATION  | XXXXXXXXXX |      -10    |    +15     |
# KLINGON_EMP |    -10     | XXXXXXXXXXX |     -5     |
# ------------|------------|-------------|------------|
#
# Translates to...
# 
# "FEDERATION,KLINGON_EMP" : -10
# "FEDERATION,VULCAN_CMD"  : +15
# "KLINGON_EMP,VULCAN_CMD" : -5