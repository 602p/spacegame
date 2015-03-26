import extention_loader, absroot, tasks, pygame, rotutil, triggers, particles
from rotutil import *
from logging import debug, info
import logging
from triggers import IS_SG_EVENT
module_logger=logging.getLogger("plugin.menu_music")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


clamp = lambda my_value, min_value, max_value: max(min(my_value, max_value), min_value)

class SoundHook_Music(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
		self.last_shields_warning=-10
		self.last_hull_warning=-10
		self.channel=pygame.mixer.Channel(0)
	def event_root(self, event):
		if IS_SG_EVENT(event):
			if event.sg_type==triggers.UE_STATE_CHANGE:
				if event.newstate.startswith('generic_ui') or \
			 event.newstate.startswith("credits") or \
			 event.newstate.startswith("dialog") or \
			 event.newstate.startswith("inventory") or \
			 event.newstate.startswith("hardpoint_select") or \
			 event.newstate == "newgame_selectship":
					self.start()
				else:
					self.end()
			if event.sg_type==triggers.UE_GAME_START:
				self.start()

	def start(self):
		debug( "Starting Menu Music..." )
		#pygame.mixer.music.load(
		if not self.channel.get_busy():
			self.channel.play(absroot.gamedb("snd_main_menu_ambiance"), -1)
		#pygame.mixer.music.play(-1)

	def end(self):
		debug( "Stopping Menu Music" )
		self.channel.stop()

def init_inject(root, console):
	info("Injecting the SoundHook")
	extention_loader.safepost(console, "[MusicManager]: Injecting the SoundHook", color=(0,255,255), bold=1)                                                                                           
	root.extentions["ambience"]=SoundHook_Music(root)