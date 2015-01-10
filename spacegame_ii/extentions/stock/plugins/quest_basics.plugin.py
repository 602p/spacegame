import primitives, ui_states

class QuestYNInterdictor(primitives.BasePrimitive):
	def run_in_event(self, event):
		def packed_y(state):
			primitives.do_group_for_event(self.root, self.config.get("event_yes", []), event)
		def packedn(state):
			primitives.do_group_for_event(self.root, self.config.get("event_no", []), event)
		ui_states.interdict_yn(root,
			self.config.get("title", "QuestYNInterdictor:title not set"),
			self.config.get("message", "QuestYNInterdictor:message not set"),
			self.config.get("button_y", "YES"),
			self.config.get("button_n", "NO"),
			packed_y,
			packed_n,
			self.config.get("textwrap", 48),
			self.config.get("modalid", "sgcui_modalyn"))

class PostIGConsoleMessage(primitives.BasePrimitive):
	def run_in_event(self, event):
		self.root.igconsole.postd(self.config, event.get_insert_dict())
	def run_in_item(self, item):
		print "printing"
		map_dict=item.get_insert_dict()
		iid=item.get_insert_dict()
		for key in iid.keys():
			map_dict["item:"+key]=iid[key]
		iid=item.parent.get_insert_dict()
		for key in iid.keys():
			map_dict["ship:"+key]=iid[key]
		if item.parent==self.root.state_manager.states["game"].player or self.config.get("postany", False):self.root.igconsole.postd(self.config, map_dict)
	def run_in_ship(self, ship):
		if ship==self.root.state_manager.states["game"].player or self.config.get("postany", False):self.root.igconsole.postd(self.config, ship.get_insert_dict())
	def run_in_impact(self, item, impact, projectile):
		map_dict={}
		iid=item.get_insert_dict()
		for key in iid.keys():
			map_dict["item:"+key]=iid[key]
		iid=impact.get_insert_dict()
		for key in iid.keys():
			map_dict["impacted:"+key]=iid[key]
		iid=projectile.get_insert_dict()
		for key in iid.keys():
			map_dict["projectile:"+key]=iid[key]
		self.root.igconsole.postd(self.config, map_dict)

def init_primitives(root, c):
	primitives.register_primitive(root, "popup_yn", QuestYNInterdictor)
	primitives.register_primitive(root, "postmsg", PostIGConsoleMessage)