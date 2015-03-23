import logging, random, absroot, primitives, ship, sectors, item, triggers, ui_states
module_logger=logging.getLogger("x.qgcourier_d")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class QGCourierDriverInit(primitives.BasePrimitive):
	def run_in_event(self, event):
		debug("Setting up a event_generic_courier_driver_init::QGCourierDriverInit")
		event.database['item_id']=random.choice([x for x in absroot.item_factories.keys() if absroot.item_factories[x].questable_for])
		event.database['tonnage']=random.randint(10,30)
		#event.database['count']=event.database['tonnage']/absroot.item_factories[event.database['item_id']].mass
		event.database['payout']=event.database['tonnage']*200
		sel_sel=random.choice(absroot.gamedb("cfg_list_spacestation_courier_destinations"))
		event.database['endpoint']=absroot.get_hid_by_selector(sel_sel)
		event.database['sector_hint']=sel_sel[sel_sel.find("@")+1:sel_sel.find(";")]
		
class QGCourierDriverStart(primitives.BasePrimitive):
	def run_in_event(self, event):
		absroot.gamestate.player.inventory.append(
			item.create_item2(event.database['item_id'],
			absroot.gamestate.player,
			count=event.database['tonnage']/absroot.item_factories[event.database['item_id']].mass
		))
		absroot.gamestate.player.add_trigger(triggers.UE_STATION_DOCK_AFTER, {
			"primitive":"event_generic_courier_driver_end",
			"ss_hid":event.database['endpoint'],
			"gq_hid":event.hid,
			"item_id":event.database['item_id'],
			"count":event.database['tonnage']/absroot.item_factories[event.database['item_id']].mass
		})

class QGCourierDriverEnd(primitives.BasePrimitive):
	def run_in_trigger(self, player, station, *a, **k):
		try:
			debug("Station hid: "+str(station.hash_id))
			debug("Req hid: "+str(self.config['ss_hid']))
			if station.hash_id==self.config['ss_hid']:
				debug("Ending quest...")
				found=0
				# print self.config
				for itemi in absroot.gamestate.player.inventory:
					if itemi.id_str==self.config["item_id"] and itemi.count>=self.config["count"]:
						found=1
						itemi.consume(self.config["count"])
				if found:
					absroot.quest_manager.get_quest(self.config["gq_hid"]).finish()
					del player.triggers[triggers.UE_STATION_DOCK_AFTER][player.triggers[triggers.UE_STATION_DOCK_AFTER].index(self.config)]
				else:
					ui_states.interdict_ok2("Quest", "You've arrived, WITHOUT THE CARGO!%nCome back when you have it!", button="OK!")
			else:
				pass
		except BaseException as e:
			print e

def init_primitives(root,console):
	primitives.register_primitive(root, "event_generic_courier_driver_init", QGCourierDriverInit)
	primitives.register_primitive(root, "event_generic_courier_driver_start", QGCourierDriverStart)
	primitives.register_primitive(root, "event_generic_courier_driver_end", QGCourierDriverEnd)