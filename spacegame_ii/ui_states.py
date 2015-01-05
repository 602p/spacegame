import state, sgc, pygame
from logging import debug, info, warning, error, critical
import os
import sys
import random

import pygame
from pygame.locals import *
try:
    from OpenGL.GL import *
except: pass

pygame.display.init()
pygame.font.init()

sys.path.insert(0, "..")

# Change directory if not running from example
p = os.path.split(sys.argv[0])[0]
if p:
    os.chdir(p)

import sgc
from sgc.locals import *

from sgc.__init__ import __version__ as ver_no



class InternalSGCMenu(sgc.Menu):
		def __init__(self, *args, **kwargs):
			self.additive_functions=kwargs["__additive_functions"]
			self.state=kwargs["__state"]
			sgc.Menu.__init__(self, *args, **kwargs)
		def func_dict(self):
			v=self.additive_functions
			v.update({
				"exit":self.state.finish,
				"print_input":self.print_inputx
				})
			return v
		def print_inputx(self):
			print self["input"].text

class GenericUIInterdictor(state.InterdictingState):
	additive_functions={}

	def start(self):
		refactored_menu=self.params["menucfg"]
		refactored_menu[0]="m:"+self.params["name"]
		self.menu=InternalSGCMenu(menu=refactored_menu, __additive_functions=self.additive_functions, __state=self)
		self.menu.additive_functions=self.additive_functions
		self._custom_image=self.root.gamedb(self.params["bg_image"])
		self.menu.add()

	def internal_update(self):
		for event in pygame.event.get():
			sgc.event(event)
		
		#self.root.screen.screen.blit(self.root.gamedb(self.params["bg_image"]), (0,0))
		sgc.update(self.root.clock.get_fps())

		self.root.fps=9999