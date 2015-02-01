import json, keymapping, ship, ui_states
from logging import debug, info, error, critical, warn

def init(root):
	root.load_modes={}
	root.savegame_migrations={}
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
		json_save=json.load(fd)
		root.savegame=SaveGame(root)
		root.savegame.load_save(json_save)

def new_game(root, start, player_name, ship_name):
	import extention_loader, sectors
	root.savegame=SaveGame(root, player_name, ship_name)
	root.dialog_manager.init_each_game()
	root.galaxy=sectors.Galaxy(root)
	root.galaxy.gamestate=root.state_manager.states["game"]
	root.state_manager.states["game"].entities=[ship.create_ship(root, start["ship"], 0, 0, ai=False)]
	root.state_manager.states["game"].player=root.state_manager.states["game"].entities[0]
	extention_loader.load_galaxy(root, 'extensions', None)
	root.galaxy.preprocess_statics()
	root.galaxy.goto_sector(*start.get("sector", [0,0]))
	root.state_manager.goto_state("game")
	root.state_manager.run_tick()
	ui_states.interdict_ok(root, title="Welcome to Spacegame!", text="Fly your ship with WASD%nSelect weapons with 1 & 2%nInteract with E%nFire with SPACE%n%n(Or rebind in the settings menu [ESC])", button = "SET")

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
			"ship_name":ship_name,
			"sector_data":{}
		}
		self.curr_revsion=2

	def get_db(self, key, default=None):
		return self.database.get(key, default)

	def save_to_config_node(self): #When we load the sector it removes all the packed entites. Need a way to get a copy from the Sector instance
		temp_db=self.database.copy()
		temp_db["packed_entities"][self.root.galaxy.get_sector().get_savegame_id()]=self.root.galaxy.get_sector().pack_entities()
		savegame={
			"savegame_revision":self.curr_revsion,
			"game_time":self.root.game_time,
			"state":"game", #Not sure if this is worth keeping
			"quest_system":None, #Not implemented!
			"database":temp_db,
			"galaxy_pos":[self.root.galaxy.currentx,self.root.galaxy.currenty],
			"player":self.root.state_manager.states["game"].player.save_to_config_node(),
			"dialog_manager":self.root.dialog_manager.save_to_config_node()
		}
		return savegame

	def load_save(self, json_save):
		import ship, sectors, extention_loader
		root=self.root
		debug("Loading Save...")

		if self.curr_revsion>json_save["savegame_revision"]:
			info("Save outdated... Migrating...")
			contupdate=1
			while contupdate:
				if json_save["savegame_revision"]+1 in self.root.savegame_migrations:
					debug("Migrating up from "+str(json_save["savegame_revision"])+' using '+str(self.root.savegame_migrations[json_save["savegame_revision"]+1])+"...")
					json_save = self.root.savegame_migrations[json_save["savegame_revision"]+1](self.root, json_save).migrate()
				else:
					contupdate=0
				if self.curr_revsion==json_save["savegame_revision"]:
					debug("Done migrating!")
					contupdate=0

		if self.curr_revsion==json_save["savegame_revision"]:
			info("Versions match, loading...")
			root.galaxy=sectors.Galaxy(root)
			root.game_time=json_save["game_time"]
			root.state_manager.states["game"].entities=[ship._load_ship(root, json_save["player"], None)]
			root.state_manager.states["game"].player=root.state_manager.states["game"].entities[0]
			
			root.savegame.database=json_save["database"]

			root.dialog_manager.do_additional_load(json_save["dialog_manager"])
			
			root.galaxy.gamestate=root.state_manager.states["game"]
			extention_loader.load_galaxy(root, 'extensions', None)

			root.galaxy.update_statics()

			root.galaxy.goto_sector(*json_save["galaxy_pos"])
			root.state_manager.goto_state("game")

		elif self.curr_revsion>json_save["savegame_revision"]:
			error("No migration path from "+str(json_save["savegame_revision"])+" --> "+str(self.curr_revsion))
			ui_states.interdict_ok(root, "LOAD ERROR", "No migration path from "+str(json_save["savegame_revision"])+" --> "+str(self.curr_revsion), "OK",
			 lambda s:s.root.state_manager.start_interdicting("generic_ui", s.root.gamedb("sgcui_mainmenu")))
		elif self.curr_revsion<json_save["savegame_revision"]:
			error("This is a save file from a newer version of Spacegame than you you have. Plz be to update")
			ui_states.interdict_ok(root, "LOAD ERROR", "This is a save file from a newer version of%n Spacegame (?!?!?!) than you you have.%n Plz be to update", "OK",
			 lambda s:s.root.state_manager.start_interdicting("generic_ui", s.root.gamedb("sgcui_mainmenu")))

class SavegameMigrator(object):
	def __init__(self, root, save):
		self.root=root
		self.save=save

	def migrate(self):
		error("Migration not defined")
		return self.save