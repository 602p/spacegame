import logging, random, absroot, primitives, ship
module_logger=logging.getLogger("x.qghunting_d")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class QGHuntingDriverInit(primitives.BasePrimitive):
	def run_in_event(self, event):
		debug("event_generic_hunting_driver_init started...")
		debug("Selecting ship...")
		debug("pool="+str(self.config["spawnpool"]))
		event.database['ship_id']=random.choice(self.config["spawnpool"])
		debug("sel="+event.database['ship_id'])
		debug("computing payout...")
		event.database['payout']=absroot.ship_factories[event.database['ship_id']].config.get("hull", 100)*random.randint(90,110)
		debug("payout="+str(event.database['payout']))
		ox=0
		# while ox==0:
			# ox=random.randint(-3,3)
		oy=0
		# while oy==0:
			# oy=random.randint(-3,3)
		event.database['sec_pos']=absroot.galaxy.sectormap[absroot.galaxy.currentx+ox][absroot.galaxy.currenty+oy].get_savegame_id()

class QGHuntingDriverStart(primitives.BasePrimitive):
	def run_in_event(self, event):
		pos_x=500#random.randint(-5000,5000)
		pos_y=500#random.randint(-5000,5000)
		debug("Starting QGHuntingDriverStart")
		debug("Spawning a "+event.database['ship_id'])
		debug("pos_x,pos_y="+str((pos_x,pos_y)))

		ship_b=ship.create_ship2(event.database['ship_id'], pos_x, pos_y)
		ship_b.add_trigger("UE_SHIP_DIE_RUN", 
			{
				"primitive":"event_generic_hunting_driver_kill",
				"hid":event.hid
			}
		)
		absroot.savegame.database["sector_data"][event.database["sec_pos"]]["packed_entities"].append(
			ship_b.save_to_config_node()
		)
		debug("Spawned")
		absroot.galaxy.reload_curr_sector()

class QGHuntingDriverKill(primitives.BasePrimitive):
	def run_in_trigger(self, *a, **k):
		absroot.quest_manager.get_quest(self.config["hid"]).finish()

def init_primitives(root,console):
	primitives.register_primitive(root, "event_generic_hunting_driver_init", QGHuntingDriverInit)
	primitives.register_primitive(root, "event_generic_hunting_driver_start", QGHuntingDriverStart)
	primitives.register_primitive(root, "event_generic_hunting_driver_kill", QGHuntingDriverKill)