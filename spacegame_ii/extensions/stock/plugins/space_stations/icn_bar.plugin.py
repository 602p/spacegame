import state, absroot, pygame
import logging, uidict
module_logger=logging.getLogger("sg.plgissc.bar")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


class BarState(state.InterdictingState):
	def first_start(self):
		self.g_config=self.params[0]
		self.config=self.params[2]
		print self.config
		self.ship=self.params[1]
		self.channel=pygame.mixer.Channel(1)
		self.channel.play(absroot.gamedb(self.config.get("ambiance", "snd_quarks_bar_ambiance")), -1)
		self.title_render=absroot.gamedb(self.g_config.get("lg_font", "font_standard_large")).render(self.g_config.get("name","[Station name not set]")+" Bar", 1, self.config.get("color",(255,255,255)))

	def internal_update(self):
		absroot.screen.screen.blit(absroot.gamedb(self.config.get("scn_image", "large_black_bg")), (0,0))

	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()

	def suspend(self):
		self.channel.stop()

def init_states(root, console):
	info("Setting up BarState")
	root.state_manager.factories["icn_ss_bar"]=state.InterdictingStateFactory(BarState)