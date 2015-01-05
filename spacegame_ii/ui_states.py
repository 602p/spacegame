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

class GenericUIInterdictor(state.InterdictingState):
	def add_widget(self, n, w):
		self.widgets[n]=w
		self.widgets[n].add()

	def del_widget(self, n):
		self.widgets[n].remove()

	def get_widget(self, n):
		return self.widgets[n]

	def remove(self):
		self.del_widget("button")

	def start(self):
		self.widgets={}

		b=sgc.Button(label="Remove")
		b.on_click=self.remove
		self.add_widget("button", b)

	def internal_update(self):
		for event in pygame.event.get():
			sgc.event(event)
		
		self.root.screen.screen.blit(self.root.gamedb(self.params["bg_image"]), (0,0))
		sgc.update(self.root.clock.get_fps())

		self.root.fps=9999