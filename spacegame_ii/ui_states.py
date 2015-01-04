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
			global SCREEN
			SCREEN=self.state.root.screen.screen
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
		self.menu=InternalSGCMenu(menu=self.params["menucfg"], __additive_functions=self.additive_functions, __state=self)
		self.menu.additive_functions=self.additive_functions
		self.menu.add()

	def internal_update(self):
		for event in pygame.event.get():
			sgc.event(event)
			#print event

		sgc.update(self.root.fps)
		self.root.fps=9999