import json, keymapping

def init(root):
	root.load_modes={}
	#register_load_mode(root, "item", item._deserialize_item)

class SerializableObject:
	def save_to_config_node(self):
		return {}

def register_load_mode(root, load_type, load_function):
	root.load_modes[load_type]=load_function

def save_game(root, filename):
	with open(filename, 'w') as fd: #json.dumps(node, indent=4)
		pass #TODO: do 

def load_game(root, filename):
	with open(filename, 'r') as fd:
		pass #TODO: do

def save_object(item):
	#assert isinstance(item, SerializableObject) #NO! DUCK TYPING IS GOD!
	return item.save_to_config_node()

def load_from_node(root, node, parent):
	return root.load_modes[node["__deserialize_handler__"]](root, node, parent)

def save_settings(settings, filename="settings.cfg"):
	del settings["keybindings"]
	with open(filename, 'w') as fd:
		json.dump(settings, fd, indent=4)

def load_settings(filename="settings.cfg"):
	with open(filename, 'r') as fd:
		o= json.load(fd)
	o["keybindings"]=keymapping.load_mapping()
	return o