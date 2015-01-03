from logging import debug, info, warning, error, critical

class BasePrimitive:
	def __init__(self, root, node):
		self.root=root
		self.config=node
		self.load_config(node)

	def load_config(self, config):
		pass

	def run_in_item(self, item):
		pass

	def run_in_event(self, event):
		pass

	def run_in_ship(self, ship):
		pass

	def run_in_impact(self, item, impact):
		self.run_in_item(item)

	def run_in_trigger(self, trigger, ship=None, item=None, impact=None, event=None):
		pass

def init(root):
	if not 'primitives' in dir(root):
		root.primitives_list={}

def register_primitive(root, name, primitive):
	root.primitives_list[name]=primitive

def get_primitive(root, name, config):
	if name in root.primitives_list.keys():
		return root.primitives_list[name](root, config)
	else:
		warning("WARNING: PRIMITIVE '"+str(name)+"' NOT DEFINED [TERMINATES PRIMITIVE CHAIN]")
		return BasePrimitive()

def do_for_item(root, name, item, node):
	get_primitive(root, name, node).run_in_item(item)

def do_for_event(root, name, event, node):
	get_primitive(root, name, node).run_in_event(event)

def do_for_ship(root, name, ship, node):
	get_primitive(root, name, node).run_in_ship(ship)

def do_for_impact(root, name, item, impacted, node):
	get_primitive(root, name, node).run_in_impact(item, impacted)

def do_for_trigger(root, name, trigger, node, ship=None, item=None, impact=None, event=None):
	get_primitive(root, name, node).run_in_trigger(trigger, ship, item, impact, event)

def do_group_for_item(root, group, item, key="primitive"):
	for i in group:
		do_for_item(root, i[key], item, i)

def do_group_for_event(root, group, event, key="primitive"):
	for i in group:
		do_for_event(root, i[key], event, i)

def do_group_for_impact(root, group, item, impacted, key="primitive"):
	for i in group:
		do_for_impact(root, i[key], item, impacted, i)

def do_group_for_ship(root, group, ship, key="primitive"):
	for i in group:
		do_for_ship(root, i[key], ship, i)

def do_group_for_trigger(root, group, trigger, ship=None, item=None, impact=None, event=None, key="primitive"):
	for i in group:
		do_for_trigger(root, i[key], trigger, i, ship, item, impact, event)