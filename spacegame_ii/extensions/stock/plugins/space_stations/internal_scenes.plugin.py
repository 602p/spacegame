import state, absroot, pygame
import logging, uidict
module_logger=logging.getLogger("sg.plgissc.dispatch")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


class DispatchState(state.InterdictingState):
	def first_start(self):
		self.config=self.params[0]
		self.ship=self.params[1]
		self.title_render=absroot.gamedb(self.config.get("lg_font", "font_standard_large")).render(self.config.get("name","[Station name not set]"), 1, self.config.get("color",(255,255,255)))

	def internal_update(self):
		absroot.screen.screen.blit(absroot.gamedb(self.config.get("bg_image", "large_black_bg")), (0,0))
		absroot.screen.screen.blit(self.title_render, (0,0))

		for subscreen_c in self.config.get("subscreens", []):
			absroot.screen.screen.blit(
				absroot.gamedb(subscreen_c["image"]),
				subscreen_c.get("pos", [100,100])
			)
			absroot.screen.screen.blit(
				absroot.gamedb(self.config.get("font", "font_standard_large")).render(subscreen_c.get("name","[subscreen_c name not set]"), 1, subscreen_c.get("color",(255,255,255))),
				(subscreen_c.get("pos", [100,100])[0]+(absroot.gamedb(subscreen_c["image"]).get_width()/2)-(absroot.gamedb(self.config.get("font", "font_standard_large")).size(subscreen_c.get("name","[subscreen_c name not set]"))[0]/2),
				 subscreen_c.get("pos", [100,100])[1]+(absroot.gamedb(subscreen_c["image"]).get_height()/2)-(absroot.gamedb(self.config.get("font", "font_standard_large")).size(subscreen_c.get("name","[subscreen_c name not set]"))[1]/2))
			)
			pygame.draw.rect(absroot.screen.screen, (255,0,0), pygame.Rect(subscreen_c.get("pos", [100,100]), absroot.gamedb(subscreen_c["image"]).get_size()), 3)


	def process_events(self, events):
		mapping={
			"store":lambda ic:absroot.state_manager.start_interdicting("inventory", {"ship":absroot.state_manager.states["game"].player, "is_shop":True, "shop_ship":self.ship}),
			"bar":lambda ic:absroot.state_manager.start_interdicting("icn_ss_bar", [self.params[0], self.params[1], ic])
		}
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
			if event.type==pygame.MOUSEBUTTONDOWN:
				if event.button==1:
					for subscreen_c in self.config.get("subscreens", []):
						if pygame.Rect(subscreen_c.get("pos", [100,100]), absroot.gamedb(subscreen_c["image"]).get_size()).collidepoint(pygame.mouse.get_pos()):
							mapping[subscreen_c["action"]](subscreen_c)

def init_states(root, console):
	info("Setting up DispatchState")
	root.state_manager.factories["plg_internal_scene_selector"]=state.InterdictingStateFactory(DispatchState)