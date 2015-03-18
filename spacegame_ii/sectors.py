from __future__ import division
import ship, json, extention_loader, triggers, pygame, serialize, logging, math
from extention_loader import HookableExtention
from triggers import *

module_logger=logging.getLogger("sg.sectors")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

SECTORSIZE=15000 #Actually 2x this
GALAXYSIZE=11 #Again, 2x this in each axis

def init(root):
	root.extentions["sector_transition_manager"]=SectorManager(root)

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
		debug("Prepopulating galaxy")
		for x in range(-GALAXYSIZE, GALAXYSIZE+1):
			self.sectormap[x]={}
			for y in range(-GALAXYSIZE, GALAXYSIZE+1):
				s=Sector(root, {"x":x,"y":y})
				self.root.savegame.database["sector_data"][s.get_savegame_id()]={}
				self.add_sector(s)
				

	def add_sector(self, sector):
		if sector.x not in self.sectormap.keys():
			self.sectormap[sector.x]={}
		#print self.root.savegame.database["sector_data"]
		if "packed_entities" not in self.root.savegame.database["sector_data"][sector.get_savegame_id()]:
			self.root.savegame.database["sector_data"][sector.get_savegame_id()]["packed_entities"]=[]
		self.sectormap[sector.x][sector.y]=sector
		sector.bind(self)

	def load_sector(self, config):
		self.add_sector(Sector(self.root, config))

	def get_sector(self):
		return self.sectormap[self.currentx][self.currenty]

	def goto_sector(self, x, y):
		info("Transitioning from sector ("+str(self.currentx)+","+str(self.currenty)+") to ("+str(x)+","+str(y)+")")
		if x in self.sectormap.keys():
			if y in self.sectormap[x].keys():
				sg_postevent(UE_CHANGE_SECTOR, galaxy=self, newx=x, newy=y)
				if type(self.currentx) == int:
					self.get_sector().unload()
				self.currentx=x
				self.currenty=y
				self.get_sector().load()
				sg_postevent(UE_CHANGE_SECTOR_FINISH, galaxy=self)
				return
		error("Sector not defined! (No change made)")

	def change_sector_by(self, x, y):
		self.goto_sector(self.currentx+x, self.currenty+y)

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

	def update_statics(self):
		info("Updating all statics...")
		for i in self.iter_sectors():
			i.update_statics()

	def tick_economy(self):
		[x.tick_economy() for x in self.iter_sectors()]

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
		self.tags = config.get("tags", [])
		self.prices = config.get("prices", {})

	def get_savegame_id(sector):
		return str(sector.x)+","+str(sector.y)

	def preprocess_statics(self):
		debug("Processing statics for sector "+self.get_savegame_id()+"...")
		#print "PROCESSING FOR "+self.get_savegame_id()
		for static in self.statics:
			#print ">>>>>>"+str(static)

			static["__deserialize_handler__"]=static["type"]
			entity = serialize.load_from_node(self.root, static, None)
			self.root.savegame.database["sector_data"][self.get_savegame_id()]["packed_entities"].append(entity.save_to_config_node())
		# if self.get_savegame_id() not in self.root.savegame.database["sector_data"].keys():
		# 	self.root.savegame.database["sector_data"][self.get_savegame_id()]={}
		self.root.savegame.database["sector_data"][self.get_savegame_id()]["last_loaded_entity"]=len(self.statics)-1

		self.root.savegame.database["sector_data"][self.get_savegame_id()]["economy"]={}
		self.update_economy()

	def update_statics(self):
		debug("Updating statics for sector "+self.get_savegame_id()+"...")
		count=0
		for static in self.statics:
			if count>self.root.savegame.database["sector_data"][self.get_savegame_id()]["last_loaded_entity"]:
				#print ">>>>>>"+str(static)
				static["__deserialize_handler__"]=static["type"]
				entity = serialize.load_from_node(self.root, static, None)
				self.root.savegame.database["sector_data"][self.get_savegame_id()]["packed_entities"].append(entity.save_to_config_node())
			count+=1

		self.root.savegame.database["sector_data"][self.get_savegame_id()]["last_loaded_entity"]=len(self.statics)-1

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
		for static in self.root.savegame.database["sector_data"][self.get_savegame_id()]["packed_entities"]:
			#static["__deserialize_handler__"]=static["type"]
			debug("Adding a PPE...")
			#print static
			entity = serialize.load_from_node(self.root, static, None)
			self.galaxy.gamestate.entities.append(entity)
		self.root.savegame.database["sector_data"][self.get_savegame_id()]["packed_entities"]=[]

	def bind(self, galaxy):
		self.galaxy=galaxy

	def unload(self):
		self.unload_entities()

	def pack_entities(self):
		packed=[]
		for entity in self.galaxy.gamestate.entities[1:]:
			if entity.can_save:
				packed.append(entity.save_to_config_node())
		return packed

	def unload_entities(self):
		self.root.savegame.database["sector_data"][self.get_savegame_id()]["packed_entities"].extend(self.pack_entities())
		self.galaxy.gamestate.player.targeted=None
		del self.galaxy.gamestate.entities[1:]


	#======Economics======

	def update_economy(self):
		debug("... Update Economy")
		for group in self.prices.keys():
			if group not in self.root.savegame.database["sector_data"][self.get_savegame_id()]["economy"]:
				debug("... Setting up economy for "+group)
				self.root.savegame.database["sector_data"][self.get_savegame_id()]["economy"][group]={
					#"group":group,
					"price":self.prices[group].get("price", 1.),
					"orig_price":self.prices[group].get("price", 1.),
					"sin_frame":0,
					"sin_speed":self.prices[group].get("speed", 1.),
					"sin_mag":self.prices[group].get("abs_mag", self.prices[group].get("price", 1.)*self.prices[group].get("rel_mag", 1.))
				}

	def tick_economy(self):
		econ_cache=self.root.savegame.database["sector_data"][self.get_savegame_id()]["economy"]
		for group, config in econ_cache.iteritems():
			# mod=math.sin(math.radians(config["sin_frame"]))*config["sin_mag"]
			# mod*=1/self.root.fps
			# config["price"]+=mod
			config["price"]=config["orig_price"]+(math.sin(math.radians(config["sin_frame"]))*config["sin_mag"]*config["sin_mag"])

			config["sin_frame"]+=(1/self.root.fps)*config["sin_speed"]

			if config["sin_frame"]>180:
				config["sin_frame"]=config["sin_frame"]-180
			
			

			# if group=='materials':
			# 	print config["price"]


	def get_commodity_mod(self, group):
		return self.root.savegame.database["sector_data"][self.get_savegame_id()]["economy"].get(group, {"price":1})["price"]

	def get_price(self, item):
		return max([self.get_commodity_mod(x) for x in item.tags])

	def get_buy_price(self, item):
		return self.get_price(item)*1.05

	def get_sell_price(self, item):
		return self.get_price(item)*0.95

class SectorManager(HookableExtention):
	def __init__(self, root):
		self.root=root

	def tick(self, state):
		if state=="game":
			player = self.root.state_manager.states["game"].player
			self.root.galaxy.tick_economy()
			#self.root.screen.draw_rect((0,255,0), pygame.Rect(-SECTORSIZE, -SECTORSIZE, SECTORSIZE, SECTORSIZE), 10)
			if player.rigidbody.x>SECTORSIZE:
				self.root.galaxy.change_sector_by(1,0)
				player.rigidbody.x=-SECTORSIZE
			if player.rigidbody.x<-SECTORSIZE:
				self.root.galaxy.change_sector_by(-1,0)
				player.rigidbody.x=SECTORSIZE
			if player.rigidbody.y>SECTORSIZE:
				self.root.galaxy.change_sector_by(0,1)
				player.rigidbody.y=-SECTORSIZE
			if player.rigidbody.y<-SECTORSIZE:
				self.root.galaxy.change_sector_by(0,-1)
				player.rigidbody.y=SECTORSIZE