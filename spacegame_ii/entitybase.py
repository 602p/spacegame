from logging import debug, warn, error, info, critical
import primitives, triggers, types, serialize, types

class Triggerable(object):
	def trigger(self, event, *args, **kw):
		if event in self.triggers.keys():
			primitives.do_group_for_trigger(self.root, self.triggers[event], *args, context=self, **kw)
		else:
			pass#warn("No triggers set up for event "+event+" (p.s. louis you should really disable this warning)")
	def serialize_triggers(self):
		return self.triggers
	def add_trigger(self, group, trigger):
		#print "Adding trigger to group "+group
		if group not in self.triggers:
			self.triggers[group]=[]
		self.triggers[group].append(trigger)

class TiggerablePosteventAdapterMixin(object):
	def sg_postevent(self, event, *args, **kw):
		triggers.sg_postevent(event, *args, **kw)
		self.trigger(event, *args, **kw)

class FlaggedEntity(Triggerable):
	can_be_targeted=False
	can_be_hit=False
	targeted=None
	selected_wep=0
	can_save=False

	def should_spawn_for_savegame(self, save):
		return None

def get_entity_by_hid(root, hid):
	hid=int(hid)

	ship = root.state_manager.states["game"]._get_entity_by_id(hid)
	if ship:
		return ship

	#Try to get it from the savegame... :/

	for secid in root.savegame.database["packed_entities"].keys():
		for packed_entity in root.savegame.database["packed_entities"][secid]:
			if packed_entity["hash_id"]==hid:
				ship = serialize.load_from_node(root, packed_entity, None)
				ship._source_sector_id=secid
				ship._source_idx=root.savegame.database["packed_entities"][secid].index(packed_entity)
				return ship

def get_hid_by_sid(root, sid):
	for ship in root.state_manager.states["game"].entities:
		if ship.id_string==sid:
			return ship.hash_id

	#Try to get it from the savegame... :/

	for secid in root.savegame.database["packed_entities"].keys():
		for packed_entity in root.savegame.database["packed_entities"][secid]:
			if packed_entity["ship_id"]==sid:
				return packed_entity["hash_id"]

def get_entity_by_sid(root, sid):
	return get_entity_by_hid(root, get_hid_by_sid(root, sid))

def init_grufs(root):
	root.get_entity_by_hid=types.MethodType(get_entity_by_hid, root)
	root.get_hid_by_sid=types.MethodType(get_hid_by_sid, root)
	root.get_entity_by_sid=types.MethodType(get_entity_by_sid, root)