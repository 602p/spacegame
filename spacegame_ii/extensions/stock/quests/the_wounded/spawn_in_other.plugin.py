import primitives, ship, random, absroot
from logging import debug, info, warn, error, critical
import entitybase as eb

class SpawnInOther(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		mapping={
			"klingonempire":"klingon_warbird",
			"federation":"federation_galaxy"
		}
		sid=False
		for faction in absroot.state_manager.states["game"].player.faction_memberships:
			if faction in mapping:
				sid=mapping[faction]
				break
		absroot.savegame.database["packed_entities"][self.config["secid"]].append(
			ship.create_ship(absroot, sid, *self.config["worldpos"]).save_to_config_node()
		)

def init_primitives(root,console):
	primitives.register_primitive(root, "UNI_wounded_spawn_ship_in_other_sector", SpawnInOther)