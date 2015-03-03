import primitives, ship, random, absroot, faction
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
		ship_b=ship.create_ship(absroot, sid, *self.config["worldpos"])
		ship_b.config["dialog_topic"]="UNI_wounded_pheonix_hail"
		ship_b.rigidbody._vector.magnitude=75
		ship_b.rigidbody._vector.angle=22
		absroot.savegame.database["packed_entities"][self.config["secid"]].append(
			ship_b.save_to_config_node()
		)

class SpawnInOther2(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		ship_b=ship.create_ship(absroot, "cardassian_freighter_UNI_wreck", *self.config["worldpos"])
		ship_b.rigidbody._vector.magnitude=75
		ship_b.rigidbody._vector.angle=22
		faction.get_faction("cardassianunion").do_join(ship_b)
		absroot.savegame.database["packed_entities"][self.config["secid"]].append(
			ship_b.save_to_config_node()
		)

def init_primitives(root,console):
	primitives.register_primitive(root, "UNI_wounded_spawn_ship_in_other_sector", SpawnInOther)
	primitives.register_primitive(root, "UNI_wounded_spawn_ship_in_other_sector2", SpawnInOther2)