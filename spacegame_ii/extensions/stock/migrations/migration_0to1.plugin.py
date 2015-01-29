import serialize
from logging import debug, info, error, critical, warn

class Migrate0To1(serialize.SavegameMigrator):
	def add_energy_config_to_ship(self, ship):
		debug("Migrating a "+ship["ship_id"]+" to add reactormax...")
		ship["currpwr"]=self.root.ship_factories[ship["ship_id"]].reactor_max
		return ship
	def migrate(self):
		debug("Migrating from 0 to 1...")
		self.save["player"]=self.add_energy_config_to_ship(self.save["player"])
		for sectorid in self.save["database"]["packed_entities"].keys():
			for ship in self.save["database"]["packed_entities"][sectorid]:
				self.save["database"]["packed_entities"][sectorid][self.save["database"]["packed_entities"][sectorid].index(ship)]=\
				 self.add_energy_config_to_ship(ship)
		self.save["savegame_revision"]=1
		return self.save

def init_migrations(root, console):
	root.savegame_migrations[1]=Migrate0To1