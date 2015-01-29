import ship, json, extention_loader, triggers, pygame, serialize
from logging import debug, info, warning, error, critical
from extention_loader import HookableExtention

SECTORSIZE=5000 #Actually 2x this

def init(root):
	root.extentions["static_entity_manager"]=SectorManager(root)

def load_file(root, fname):
	debug("Load sector_file '"+fname)
	with open(fname, 'r') as f:
		root.galaxy.load_sector(json.load(f))

def add_static_creator(root, key, func):
	root.static_creators[key]=func

def _create_ship_static(root, sector, config):
	ship_o = ship.create_ship(root, config["id"], config.get("x", 0), config.get("y", 0),
		config.get("equipment", True), config.get("ai", True))
	return ship_o

class Galaxy(object):
	def __init__(self, root):
		self.currentx=None
		self.currenty=None
		self.root=root
		self.gamestate=None
		self.sectormap={} #[x][y]

	def add_sector(self, sector):
		if sector.x not in self.sectormap.keys():
			self.sectormap[sector.x]={}
		if sector.get_savegame_id() not in self.root.savegame.database["packed_entities"]:
			self.root.savegame.database["packed_entities"][sector.get_savegame_id()]=[]
		self.sectormap[sector.x][sector.y]=sector
		sector.bind(self)

	def load_sector(self, config):
		self.add_sector(Sector(self.root, config))

	def get_sector(self):
		return self.sectormap[self.currentx][self.currenty]

	def goto_sector(self, x, y):
		info("Transitioning from sector ("+str(self.currentx)+","+str(self.currenty)+") to ("+str(x)+","+str(y)+")")

		if type(self.currentx) == int:
			self.get_sector().unload()
		self.currentx=x
		self.currenty=y
		self.get_sector().load()

	def iter_sectors(self):
		l=[]
		for k in self.sectormap.keys():
			for k2 in self.sectormap[k].keys():
				l.append(self.sectormap[k][k2])
		return l

	def preprocess_statics(self):
		info("Preprocessing all statics...")
		for i in self.iter_sectors():
			i.preprocess_statics()

class Sector(object):
	def __init__(self, root, config):
		self.x=config["x"]
		self.y=config["y"]
		self.root=root
		self.galaxy=None
		self.name=config.get("name", "Sector "+str(self.x)+", "+str(self.y))
		self.faction=config.get("faction", "null_faction")
		self.enter_effects=config.get("enter_effects", [])
		self.leave_effects=config.get("leave_effects", [])
		self.statics = config.get("statics", [])

	def get_savegame_id(sector):
		return str(sector.x)+","+str(sector.y)

	def preprocess_statics(self):
		debug("Processing statics for sector "+self.get_savegame_id()+"...")
		for static in self.statics:
			static["__deserialize_handler__"]=static["type"]
			entity = serialize.load_from_node(self.root, static, None)
			self.root.savegame.database["packed_entities"][self.get_savegame_id()].append(entity.save_to_config_node())

	def load(self):
		self.root.igconsole.post("Now entering "+self.name+"...", bold=1, color=(0,255,0))
		self.load_entities()

	def load_entities(self):
		debug("Processing entities for sector:"+self.name)
		# for static in statics:
		# 	static["__deserialize_handler__"]=static["type"]
		# 	entity = serialize.load_from_node(self.root, static, None)
		# 	name = str(self.x)+","+str(self.y)+static.get("name", "UNNAMEDSTATIC_"+str(statics.index(static)))
		# 	should_spawn=entity.should_spawn_for_savegame(self.root.savegame)
		# 	debug("Processing static {"+name+"}:"+str(entity))
		# 	if should_spawn==True:
		# 		self.entities[name]=entity
		# 		debug("--(Added)")
		# 	elif should_spawn==None:
		# 		if name not in self.root.savegame.get_db("removed_statics"):
		# 			self.galaxy.gamestate.entities.append(entity)
		# 			self.entities[name]=entity
		# 			debug("--(Added)")
		# 		else:
		# 			debug("--(Not adding static, should_spawn neutral, in removed_statics)")
		# 	else:
		# 		debug("--(Not adding static, should_spawn disabled)")
		for static in self.root.savegame.database["packed_entities"][self.get_savegame_id()]:
			#static["__deserialize_handler__"]=static["type"]
			debug("Adding a PPE...")
			entity = serialize.load_from_node(self.root, static, None)
			self.galaxy.gamestate.entities.append(entity)
		self.root.savegame.database["packed_entities"][self.get_savegame_id()]=[]

	def bind(self, galaxy):
		self.galaxy=galaxy

	def unload(self):
		self.unload_entities()

	def unload_entities(self):
		for entity in self.galaxy.gamestate.entities[1:]:
			if entity.can_save:
				self.root.savegame.database["packed_entities"][self.get_savegame_id()].append(entity.save_to_config_node())
		self.galaxy.gamestate.player.targeted=None
		del self.galaxy.gamestate.entities[1:]

class SectorManager(HookableExtention):
	def __init__(self, root):
		self.root=root

	def tick(self, state):
		if state=="game":
			player = self.root.state_manager.states["game"].player
			#self.root.screen.draw_rect((0,255,0), pygame.Rect(-SECTORSIZE, -SECTORSIZE, SECTORSIZE, SECTORSIZE), 10)
			if player.rigidbody.x>SECTORSIZE:
				pass