import json, keymapping, ship, ui_states

def init(root):
	root.load_modes={}
	#register_load_mode(root, "item", item._deserialize_item)

class SerializableObject:
	def save_to_config_node(self):
		return {'__deserialize_handler__':'dont'}

def register_load_mode(root, load_type, load_function):
	root.load_modes[load_type]=load_function

def save_game(root, filename):
	with open(filename, 'w') as fd: #json.dumps(node, indent=4)
		json.dump(root.savegame.save_to_config_node(), fd, indent=4)

def load_game(root, filename):
	with open(filename, 'r') as fd:
		pass #TODO: do

def new_game(root, start, player_name, ship_name):
	import extention_loader, sectors
	root.savegame=SaveGame(root, player_name, ship_name)
	root.galaxy=sectors.Galaxy(root)
	root.galaxy.gamestate=root.state_manager.states["game"]
	root.state_manager.states["game"].entities=[ship.create_ship(root, start["ship"], 0, 0, ai=False)]
	root.state_manager.states["game"].player=root.state_manager.states["game"].entities[0]
	extention_loader.load_galaxy(root, 'extensions', None)
	root.galaxy.preprocess_statics()
	root.galaxy.goto_sector(*start.get("sector", [0,0]))
	root.state_manager.goto_state("game")
	root.state_manager.run_tick()
	ui_states.interdict_ok(root, title="Welcome to Spacegame!", text="Fly your ship with WASD%nSelect weapons with 1 & 2%nInteract with E%nFire with SPACE%n%n(Or rebind in the settings menu [ESC])")

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
	o["keybindings"]=keymapping.load_mapping(o["keymapping_file"])
	return o

class SaveGame(object, SerializableObject):
	def __init__(self, root, player_name="pn", ship_name="sn"):
		self.root=root
		self.database={
			"packed_entities":{},
			"player_name":player_name,
			"ship_name":ship_name
		}

	def get_db(self, key, default=None):
		return self.database.get(key, default)

	def save_to_config_node(self): #When we load the sector it removes all the packed entites. Need a way to get a copy from the Sector instance
		savegame={
			"savegame_revision":0,
			"game_time":self.root.game_time,
			"state":"game",
			"quest_system":None, #Not implemented!
			"database":self.database,
			"galaxy_pos":[self.root.galaxy.currentx,self.root.galaxy.currenty],
			"player":self.root.state_manager.states["game"].player.save_to_config_node()
		}
		return savegame