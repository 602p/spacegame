import state, absroot, pygame, ui_states, item, sgc
import logging, uidict, quests, random, tooltips, types
module_logger=logging.getLogger("sg.plgissc.hangar2s")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class HangarState2(ui_states.JSONGenericUIStateMixin):
	def first_start(self):
		self.ui_widgets=absroot.gamedb("sgcui_icn_hangar2")["widgets"]
		self.ui_bg=self.params[2]["scn_image"]
		self.data_inserts={"hangar_name":self.params[0].get("name","[Station name not set]")+" Hangar"}
		self.init_ui()

	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
		self.update_ui(events)

def init_states(root, console):
	info("Setting up HangarState2")
	root.state_manager.factories["icn_ss_hangar2"]=state.InterdictingStateFactory(HangarState2)