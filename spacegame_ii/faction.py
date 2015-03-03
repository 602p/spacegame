import json, jsonutil, absroot, primitives, tooltips
from logging import debug, info, warn, error, critical
from triggers import *
import logging
module_logger=logging.getLogger("sg.faction")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	root.factions={}
	#

def load_file(root, fn):
	debug("Loading faction_file: "+fn)
	with open(fn, 'r') as fd:
		jsone=jsonutil.get_expanded_json(root.gamedb, json.load(fd))
		root.factions[jsone["id"]] = Faction(jsone)

def get_faction(name):
	return absroot.factions[name]

class Faction(tooltips.GenericTooltipMixin):
	def __init__(self, config):
		self.config=config
		self.id_str=config["id"]
		self.name=config.get("name", "UNS_name")
		self.longname=config.get("longname","["+self.name+"]")
		self.description=config.get("description", "UNS_description")
		self.color=config.get("color", [40,40,40])
		self.tags=config.get("tags",[])
		self.join_required=config.get("join_requirements",[])
		self.leave_required=config.get("leave_requirements",[])
		self.join_effects=config.get("join_effects",[])
		self.leave_effects=config.get("leave_effects",[])
		self.relations=config.get("relations",{})
		self.visible=config.get("visible", True)
		if self.visible:
			self.icon_image=absroot.gamedb(config.get("icon_image", "$BLANK"))
			self.banner_image=absroot.gamedb(config.get("banner_image", "$BLANK"))
		#print config

	def do_join(self, ship, force_functional=False):
		primitives.do_group_for_ship(absroot, self.join_effects, ship)
		sg_postevent(UE_FACTION_JOINED, faction=self, ship=ship)
		debug("A "+ship.id_str+" joined "+self.id_str+" [functional]")
		if (self.id_str not in ship.faction_memberships) and not force_functional:
			ship.faction_memberships.append(self.id_str)
			sg_postevent(UE_FACTION_JOINED_LOGIC, faction=self, ship=ship)
			debug("A "+ship.id_str+" joined "+self.id_str+" [logical]")

	def can_join(self, ship):
		return primitives.do_group_for_ship(absroot, self.join_required, ship)

	def try_join(self, ship):
		if self.can_join(ship):
			self.do_join(ship)
			return True
		return False

	def do_leave(self, ship, force_functional=False):
		primitives.do_group_for_ship(absroot, self.leave_effects, ship)
		sg_postevent(UE_FACTION_LEFT, faction=self, ship=ship)
		debug("A "+ship.id_str+" left "+self.id_str)
		if (self.id_str in ship.faction_memberships):
			del ship.faction_memberships[ship.faction_memberships.index(self.id_str)]

	def can_leave(self, ship):
		return primitives.do_group_for_ship(absroot, self.leave_required, ship)

	def try_leave(self, ship):
		if self.can_leave(ship):
			self.do_leave(ship)
			return True
		return False

	def tt_render_image(self):
		self.tt_image_init((1000,1000))
		self.tt_image.blit(self.banner_image, (0,0))
		self.tt_image.blit(absroot.gamedb("font_item_title").render(self.name, 1, self.color), (70,0))
		self.tt_image.blit(
			tooltips.render_wrapped_text("("+self.longname+")\n"+self.description, 400, absroot.gamedb("font_item_desc"), (40,40,40))
			,(70, absroot.gamedb("font_item_title").size("|")[1]))
		self.tt_image_clip()
		self.tt_add_box()


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
	def load_from_config_node(paul_blart_meme_man_our_god_all_hail_he_is_great_and_so_amazing_PAUL_BLART_HELL_YEAH_all_hail, node):
		temp = paul_blart_meme_man_our_god_all_hail_he_is_great_and_so_amazing_PAUL_BLART_HELL_YEAH_all_hail(absroot)
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