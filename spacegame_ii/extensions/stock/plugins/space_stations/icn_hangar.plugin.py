import state, absroot, pygame, ui_states, item
import logging, uidict, quests, random, tooltips
module_logger=logging.getLogger("sg.plgissc.bar")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class _GenericButton(tooltips.ReloadOnMouseOverTooltipMixin):
	desc_text="???"
	def __init__(self, name, color, pos):
		self.name=name
		self.color=color
		self.size=absroot.gamedb("font_item_title").size(name)
		self.pos=pos
		self.rect=pygame.Rect(pos, self.size)

	def render(self):
		pygame.draw.rect(absroot.screen.screen, self.color, self.rect)
		absroot.screen.screen.blit(absroot.gamedb("font_item_title").render(self.name, 1, (0,0,0)), self.rect)

	def on_click(self):
		for item in absroot.gamestate.player.inventory:
			if item.id_str=="money":
				if item.count>=self.get_cost():
					def _y(s):
						item.count-=self.get_cost()
						self.do_action()
					ui_states.interdict_yn2("Repair", "Are you sure?", button_y="Yes", button_n="No", callback_y=_y)
					return
		ui_states.interdict_ok2("Repair", "Ye dinnae have the cash laddie%n(Why did I make this scottish?)", button="Goodbye")

	def tt_render_image(self):
		self.tt_image_init((1000,1000))

		self.tt_image.blit(absroot.gamedb("font_item_title").render(self.desc_text, 1, (20,20,20)), (0,0))
		self.tt_image.blit(
			absroot.gamedb("font_item_desc").render("Cost: "+str(self.get_cost()), 1, (20,20,20)),
			(0,absroot.gamedb("font_item_title").size("|")[1]))

		self.tt_image_clip()
		self.tt_add_box()

class _RepairHullButton(_GenericButton):
	desc_text="Repair hull"
	def get_cost(self):
		return (absroot.gamestate.player.damage.maxhull-absroot.gamestate.player.damage.hull)*20
	def do_action(self):
		absroot.state_manager.states["game"].player.damage.hull=absroot.state_manager.states["game"].player.damage.maxhull
		ui_states.interdict_ok2("Repair", "Your hull has been fully repaired", button="Goodbye")

class _RepairOneHullButton(_GenericButton):
	desc_text="Repair one hull point"
	def get_cost(self):
		return 20
	def do_action(self):
		absroot.state_manager.states["game"].player.damage.hull+=1
		if absroot.state_manager.states["game"].player.damage.hull>absroot.state_manager.states["game"].player.damage.maxhull:
			absroot.state_manager.states["game"].player.damage.hull=absroot.state_manager.states["game"].player.damage.maxhull
		ui_states.interdict_ok2("Repair", "Your hull has been repaired a bit", button="Goodbye")

class _RepairSystemsButton(_GenericButton):
	desc_text="Repair all Subsystems"
	def get_cost(self):
		return len([x for x in [x for x in absroot.state_manager.states["game"].player.damage.systems if x] if x.health!=x.maxhealth])*20
	def do_action(self):
		for i in absroot.state_manager.states["game"].player.damage.systems:
			if i:
				i.deal_damage(-10000)
		ui_states.interdict_ok2("Repair", "All your Subsystems have been fully repaired", button="Goodbye")

class HangarState(state.InterdictingState):
	def first_start(self):
		debug("Starting HangarState")
		self.g_config=self.params[0]
		self.config=self.params[2]
		self.ship=self.params[1]
		self.title_render=absroot.gamedb(self.g_config.get("lg_font", "font_standard_large")).render(self.g_config.get("name","[Station name not set]")+" Hangar", 1, self.config.get("color",(255,255,255)))

		self.buttons=[
			_RepairHullButton("Repair Hull", (0,200,0), (500,200)),
			_RepairSystemsButton("Repair Subsystems", (0,0,200), (650,200)),
			_RepairOneHullButton("Repair One Hull", (200,0,0), (500,250)),
		]

	def internal_update(self):
		absroot.screen.screen.blit(absroot.gamedb(self.config.get("scn_image", "large_black_bg")), (0,0))
		absroot.screen.screen.blit(self.title_render, (0,0))

		for button in self.buttons:
			button.render()
			button.tt_delay_update(button.rect)

	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
			if event.type==pygame.MOUSEBUTTONDOWN:
				if event.button==1:
					collisions=[x for x in self.buttons if x.rect.collidepoint(pygame.mouse.get_pos())]
					for button in collisions:
						button.on_click()

def init_states(root, console):
	info("Setting up HangarState")
	root.state_manager.factories["icn_ss_hangar"]=state.InterdictingStateFactory(HangarState)