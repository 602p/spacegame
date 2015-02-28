
#====
from __future__ import division
import logging, state, absroot, pygame, extention_loader, primitives
module_logger=logging.getLogger("sg.x.cutsceneMPG")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class MPGCutscenePlayer(state.InterdictingState):
	def first_start(self):
		debug("Starting MPGCutscenePlayer")
		self.config=absroot.gamedb(self.params)
		assert "x_type" in self.config, "Is this actually a cutscene you gave me??"
		assert self.config["x_type"]=="cutscene", "Is this actually a cutscene you gave me?? [2]"
		path=absroot.gamedb.get_meta(self.params)["basepath"]+self.config["path"]
		debug("Loading path: "+path)
		self.movie=pygame.movie.Movie(path)
		if not self.config.get("mute"):
			pygame.mixer.quit()

		self.movie_screen=pygame.Surface(absroot.renderspace_size).convert()
		self.movie.set_display(self.movie_screen, pygame.Rect((0,0), absroot.renderspace_size))
		self.time=0.0
		self.movie.skip(self.config.get("clipping", [0,0])[0])
		self.movie.play()
		debug("Movie started")

	def internal_update(self):
		self.time+=1/absroot.clock.get_fps()
		absroot.screen.screen.blit(self.movie_screen, (0,0))
		if self.time > self.config.get("clipping", [0,999999999])[1] or not self.movie.get_busy():
			self.movie.stop()
			self.finish()
			debug("Movie finished")

	def process_events(self, events):
		for e in events:
			if e.type==pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					self.movie.stop()
					debug("Pressed ESC to stop movie")

class MPGCutscenePlayerPrimitive(primitives.BasePrimitive):
	def run(self):
		absroot.state_manager.start_interdicting("cutscene", self.config["movie"])

	def run_in_item(self, *a, **k):
		self.run()

	def run_in_impact(self, *a, **k):
		self.run()

	def run_in_faction(self, *a, **k):
		self.run()

	def run_in_ship(self, *a, **k):
		self.run()

def init_state(self, console):
	extention_loader.safepost(console, "[stock]: Adding the MPGCutscenePlayer StateFactory", color=(0,255,255), bold=1)
	debug("Adding the state")
	absroot.state_manager.factories["cutscene"]=state.InterdictingStateFactory(MPGCutscenePlayer)
	primitives.register_primitive(absroot, "play_cutscene", MPGCutscenePlayerPrimitive)