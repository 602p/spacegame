from logging import debug, info, warning, error, critical
import logging
module_logger=logging.getLogger("sg.primitives")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


class BasePrimitive:
	primitive_id="_BasePrimitive"
	def __init__(self, root, node):
		self.root=root
		self.config=node
		self.load_config(node)
		#print "Created a "+self.primitive_id

	@classmethod
	def _bind(self, idx):
		self.primitive_id=idx

	def load_config(self, config, *args):
		pass

	def run_in_item(self, item, *args):
		warning("Behavior for "+self.primitive_id+" is undefined in context [item], running as default")
		self.run_in_default()

	def run_in_event(self, event, *args):
		warning("Behavior for "+self.primitive_id+" is undefined in context [event], running as default")
		self.run_in_default()

	def run_in_ship(self, ship, *args):
		warning("Behavior for "+self.primitive_id+" is undefined in context [ship], running as default")
		self.run_in_default()

	def run_in_impact(self, item, impact, projectile=None, *args):
		warning("Behavior for "+self.primitive_id+" is undefined in context [impact], running as item")
		self.run_in_item(item)

	def run_in_sector(self, sector, *args):
		warning("Behavior for "+self.primitive_id+" is undefined in context [sector], running as default")
		self.run_in_default()

	def run_in_dialog(self, dialog, speech, *args):
		return True

	def run_in_trigger(self, *args, **kw):
		warning("Behavior for "+self.primitive_id+" is undefined in context [trigger], running as default")
		self.run_in_default()

	def run_in_faction(self, faction):
		warning("Behavior for "+self.primitive_id+" is undefined in context [faction], running as default")
		self.run_in_default()

	def run_in_default(self):
		warning("Behavior for "+self.primitive_id+" is undefined in context [default]")

def init(root):
	if not 'primitives' in dir(root):
		root.primitives_list={}

def register_primitive(root, name, primitive):
	debug("Registering primitive "+name+" ("+str(primitive)+")")
	root.primitives_list[name]=primitive
	primitive._bind(name)

def get_primitive(root, name, config):
	if name in root.primitives_list.keys():
		#debug("getting primitive "+name)
		return root.primitives_list[name](root, config)
	else:
		warning("WARNING: PRIMITIVE '"+str(name)+"' NOT DEFINED")
		return BasePrimitive(root, config)

def do_for_item(root, name, item, node):
	return get_primitive(root, name, node).run_in_item(item)

def do_for_event(root, name, event, node):
	return get_primitive(root, name, node).run_in_event(event)

def do_for_ship(root, name, ship, node):
	return get_primitive(root, name, node).run_in_ship(ship)

def do_for_impact(root, name, item, impacted, projectile, node):
	return get_primitive(root, name, node).run_in_impact(item, impacted, projectile)

def do_for_sector(root, name, sector, node):
	return get_primitive(root, name, node).run_in_sector(sector)

def do_for_trigger(root, name, node, *args, **kw):
	return get_primitive(root, name, node).run_in_trigger(*args, **kw)

def do_for_dialog(root, name, dialog, speech, node):
	return get_primitive(root, name, node).run_in_dialog(dialog, speech)

def do_for_faction(root, name, faction, node):
	return get_primitive(root, name, node).run_in_faction(faction)

def do_group_for_item(root, group, item, key="primitive"):
	c=1
	for i in group:
		if not do_for_item(root, i[key], item, i):
			c=0
	return c

def do_group_for_event(root, group, event, key="primitive"):
	c=1
	for i in group:
		if not do_for_event(root, i[key], event, i):
			c=0
	return c

def do_group_for_impact(root, group, item, impacted, projectile=None, key="primitive"):
	c=1
	for i in group:
		if not do_for_impact(root, i[key], item, impacted, projectile, i):
			c=0
	return c

def do_group_for_ship(root, group, ship, key="primitive"):
	c=1
	for i in group:
		if not do_for_ship(root, i[key], ship, i):
			c=0
	return c

def do_group_for_faction(root, group, faction, key="primitive"):
	c=1
	for i in group:
		if not do_for_faction(root, i[key], faction, i):
			c=0
	return c

def do_group_for_sector(root, group, sector, key="primitive"):
	c=1
	for i in group:
		if not do_for_sector(root, i[key], sector, i):
			c=0
	return c

def do_group_for_trigger(root, group, *args, **kwargs):
	c=1
	for i in group:
		if not do_for_trigger(root, i["primitive"], i, *args, **kwargs):
			c=0
	return c

def do_group_for_dialog(root, group, dialog, speech, key="primitive"):
	c=1
	for i in group:
		if not do_for_dialog(root, i[key], dialog, speech, i):
			c=0
	return c

#         do_group_for_item
#                 |
#                / \
#               /   \
#              V     V
#   sound_effect     fire_projectile
#                           |
#                         on_hit -------------> trigger
#                           |                      |
#                          / \----------------\    \---------------\--------------------\
#                         /   \                \                    \                    \
#                        V     V                V                    V                    V
#            simple_damage     play_animation   sound_effect         sound_effect         delayed_sound_effect