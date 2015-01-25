import primitives, ui_states, formatting
from logging import debug, info, warning, error, critical

class QuestYNInterdictor(primitives.BasePrimitive):
	def run_in_event(self, event):
		def packed_y(state):
			primitives.do_group_for_event(self.root, self.config.get("event_yes", []), event)
		def packed_n(state):
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

class QuestOKInterdictor(primitives.BasePrimitive):
	def run(self):
		#print "popup_ok called"
		ui_states.interdict_ok_node(self.root, self.config)
	def run_in_event(self, *a, **b):
		self.run()
	def run_in_item(self, *a, **b):
		self.run()
	def run_in_ship(self, *a, **b):
		self.run()
	def run_in_impact(self, *a, **b):
		self.run()

class PostIGConsoleMessage(primitives.BasePrimitive):
	def run_in_event(self, event):
		self.root.igconsole.postd(self.config, formatting.SubFormatter(self.root.formatter,{
			"event":event
		}))

	def run_in_item(self, item):
		if item.parent==self.root.state_manager.states["game"].player or self.config.get("postany", False):
			self.root.igconsole.postd(self.config, formatting.SubFormatter(self.root.formatter,{
				"item":item,
				"ship":item.parent
			}))

	def run_in_ship(self, ship):
		if ship==self.root.state_manager.states["game"].player or self.config.get("postany", False):
			self.root.igconsole.postd(self.config, formatting.SubFormatter(self.root.formatter,{
				"ship":ship
			}))

	def run_in_impact(self, item, impact, projectile):
		if projectile.parent==self.root.state_manager.states["game"].player or self.config.get("postany", False):
			self.root.igconsole.postd(self.config, formatting.SubFormatter(self.root.formatter,{
				"item":item,
				"hit_ship":impact,
				"projectile":projectile,
				"projectile_ship":projectile.parent.parent
			}))

class RequireWeaponTagged(primitives.BasePrimitive):
	def do_for_event(self, event):
		#TODO: Make actually work
		warn("RequireWeaponTagged [require_weapon_tagged] NOT IMPLEMENTED")
		return 1

def init_primitives(root, c):
	primitives.register_primitive(root, "popup_yn", QuestYNInterdictor)
	primitives.register_primitive(root, "popup_ok", QuestOKInterdictor)
	primitives.register_primitive(root, "postmsg", PostIGConsoleMessage)
	primitives.register_primitive(root, "require_weapon_tagged", RequireWeaponTagged)