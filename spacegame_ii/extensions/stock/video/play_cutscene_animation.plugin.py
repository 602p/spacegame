from __future__ import division
import logging, state, absroot, pygame, extention_loader, primitives
module_logger=logging.getLogger("sg.x.cutsceneANIM")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class ANIMCutscenePlayer(state.InterdictingState):
	def first_start(self):
		debug("Starting ANIMCutscenePlayer")
		self.config=absroot.gamedb(self.params)
		self.frames=[[absroot.gamedb(x), y] for [x,y] in self.config["frames"]]
		self.time=0.
		self.current=0

	def internal_update(self):
		self.time+=1/absroot.clock.get_fps()
		absroot.screen.screen.blit(self.frames[self.current][0], (0,0))
		if self.time>self.frames[self.current][1]:
			self.time=0.
			self.current+=1
			if self.current==len(self.frames):
				self.finish()

	def process_events(self, events):
		for e in events:
			if e.type==pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					self.finish()
					debug("Pressed ESC to stop movie")

class ANIMCutscenePlayerPrimitive(primitives.BasePrimitive):
	def run(self):
		absroot.state_manager.start_interdicting("cutscene_anim", self.config["anim"])

	def run_in_item(self, *a, **k):
		self.run()

	def run_in_impact(self, *a, **k):
		self.run()

	def run_in_faction(self, *a, **k):
		self.run()

	def run_in_ship(self, *a, **k):
		self.run()

def init_state(self, console):
	extention_loader.safepost(console, "[stock]: Adding the ANIMCutscenePlayer StateFactory", color=(0,255,255), bold=1)
	debug("Adding the state")
	absroot.state_manager.factories["cutscene_anim"]=state.InterdictingStateFactory(ANIMCutscenePlayer)
	primitives.register_primitive(absroot, "play_cutsceneanim", ANIMCutscenePlayerPrimitive)
