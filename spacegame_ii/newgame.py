from logging import debug, info, warning, error, critical
import state, pygame, ui_states, serialize, absroot, random
from toolbox import EasyGame
import logging
module_logger=logging.getLogger("sg.newgame")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	root.widget_controllers.update({
		"nginputs_controller":NGInputsController,
		"create_new_save":CreateNewSave,
		"do_save_game":SaveCurrentGame
	})

def show_tip():
	debug("show_tip called:")
	tips=[]
	[tips.extend(x) for x in absroot.gamedb.get_startswith("tipsntricks_")]
	tip=random.choice(tips)
	debug("  picked tip: "+tip)
	if absroot.settings["gameplay"]["tips"]:
		ui_states.interdict_ok2(title="Tip", text=tip+"\n\n\nThis can be disabled in Settings", button="Close")
		debug("  popped")
	else:debug("  (disabled)")

class ShipSelectState(state.State):
	def first_start(self):
		debug("ShipSelectState starting...")
		self.starts=self.root.gamedb.get_startswith("startdefun_")

	def update_and_render(self):
		screen=self.root.screen.screen
		currx=0
		screen.blit(self.root.gamedb("large_black_bg"), (0,0))
		for start in self.starts:
			screen.blit(self.root.gamedb(start["banner"]), (currx,0))
			screen.blit(self.root.gamedb(start["font"]).render(start["name"], 1, start.get("namecolor", (255,255,255))), (currx, 600))
			if pygame.Rect(currx, 0, 300, 600).collidepoint(pygame.mouse.get_pos()):
				if pygame.mouse.get_pressed()[0]:
					builtdict=self.root.gamedb("sgcui_newgame_inputs")
					builtdict["_startcfg"]=start
					self.root.state_manager.start_interdicting("generic_ui", builtdict)
			currx+=333
		screen.blit(self.root.gamedb("uia_back_button"), (0,640))
		if pygame.Rect(0,640,60,60).collidepoint(pygame.mouse.get_pos()):
			if pygame.mouse.get_pressed()[0]:
				self.root.state_manager.start_interdicting("generic_ui", self.root.gamedb("sgcui_mainmenu"))

class NGInputsController(ui_states.WidgetController):
	def on_start(self):
		self.state.widgets["description"].config(
			text=self.state.params["_startcfg"].get("description", "NO DESC").replace("%n","\n")
		)

class CreateNewSave(ui_states.WidgetController):
	def on_click(self):
		serialize.new_game(self.root, self.state.params["_startcfg"], self.state.widgets["playername"].text, self.state.widgets["shipname"].text)
		if self.root.settings["gameplay"]["intro_popup"]:
			ui_states.interdict_ok(self.root, title="Welcome to Spacegame!", text="Fly your ship with WASD%nSelect weapons with 1 & 2%nInteract with E%nTalk to selected with F%nFire with SPACE%n%n(Or rebind in the settings menu [ESC])", button = "Start!")
		show_tip()

class SaveCurrentGame(ui_states.WidgetController):
	def on_click(self):
		serialize.save_game(self.root, EasyGame.pathgetter("saves/", 1, "Select a file to save to..."))