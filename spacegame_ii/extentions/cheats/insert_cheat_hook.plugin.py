import extention_loader, pygame, ui_states, item
from logging import debug, info, warning, error, critical

KEY_CODE=pygame.K_F10

class CheatHook(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if state=="game":
			if event.type==pygame.KEYDOWN:
				if event.key==KEY_CODE:
					self.root.state_manager.start_interdicting("generic_ui", self.root.gamedb("x_cheats_gui"))
	def last_load(self):
		debug("Adding WidgetControllers")
		self.root.widget_controllers["xcheat_repair_player"]=RepairPlayerShip
		self.root.widget_controllers["xcheat_mirror_player_collideability"]=MirrorPlayerCollideability
		self.root.widget_controllers["xcheat_add_item"]=CreateItem
		self.root.widget_controllers["xcheat_set_attribute"]=SetPlayerAttribute
		self.root.widget_controllers["xcheat_get_attribute"]=GetPlayerAttribute
		self.root.widget_controllers["xcheat_rebuild_systems"]=RebuildSystems

class RepairPlayerShip(ui_states.WidgetController):
	def on_click(self):
		self.root.state_manager.states["game"].player.damage.hull=self.root.state_manager.states["game"].player.damage.maxhull
		for i in self.root.state_manager.states["game"].player.damage.systems:
			if i:
				i.deal_damage(-10000)

class MirrorPlayerCollideability(ui_states.WidgetController):
	def on_click(self):
		self.root.state_manager.states["game"].player.can_be_hit=self.widget.state

	def on_start(self):
		self.widget.config(state=self.root.state_manager.states["game"].player.can_be_hit)

class CreateItem(ui_states.WidgetController):
	def on_click(self):
		if self.state.widgets[self.config["delete_old"]].state:
			del self.root.state_manager.states["game"].player.inventory[self.root.state_manager.states["game"].player.inventory.index(
			  self.root.state_manager.states["game"].player.get_item_in_hardpoint(int(self.state.widgets[self.config["equip"]].text)))]
		myitem = item.create_item(self.root, self.state.widgets[self.config["id"]].text, self.root.state_manager.states["game"].player, int(self.state.widgets[self.config["equip"]].text))
		myitem.count=int(self.state.widgets[self.config["count"]].text)
		self.root.state_manager.states["game"].player.inventory.append(myitem)

class SetPlayerAttribute(ui_states.WidgetController):
	def on_click(self):
		data=self.state.widgets[self.config["attr_value"]].text
		if self.state.widgets[self.config["attr_eval"]].state:
			data=eval(data)
		target=self.state.widgets[self.config["attr_target"]].selection
		if target==0:
			target=self.root.state_manager.states["game"].player
		elif target==1:
			target=self.root.state_manager
		elif target==2:
			target=self.root.state_manager.states["game"]
		elif target==3:
			target=self.root
		exec "target."+self.state.widgets[self.config["attr_name"]].text+"=data"
		
		

class GetPlayerAttribute(ui_states.WidgetController):
	def on_click(self):
		target=self.state.widgets[self.config["attr_target"]].selection
		if target==0:
			target=self.root.state_manager.states["game"].player
		elif target==1:
			target=self.root.state_manager
		elif target==2:
			target=self.root.state_manager.states["game"]
		elif target==3:
			target=self.root
		data=eval("target."+self.state.widgets[self.config["attr_name"]].text)
		self.state.widgets[self.config["attr_value"]].config(text=str(data))

class RebuildSystems(ui_states.WidgetController):
	def on_click(self):
		self.root.state_manager.states["game"].player.damage.rebuild_systems()

def init_inject(root, console):
	info("Injecting the CheatHook")
	extention_loader.safepost(console, "[cheats:insert_cheat_hook]: Injecting the CheatHook", color=(0,255,255), bold=1)
	root.extentions["cheathook"]=CheatHook(root)