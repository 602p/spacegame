
class FlaggedEntity(object):
	can_be_targeted=False
	can_be_hit=False
	targeted=None
	selected_wep=0
	can_save=False
	def should_spawn_for_savegame(self, save):
		return None