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

	def repair_hull(self):
		self.state_manager.states["game"].player.damage.hull=self.state_manager.states["game"].player.damage.maxhull

	def repair_systems(self):
		for i in self.state_manager.states["game"].player.damage.systems:
			if i:
				i.deal_damage(-10000)

	def start(self):
		self.widgets={}

		b=sgc.Button(label="Remove")
		b.on_click=self.remove
		self.add_widget("button", b)

		b=sgc.Button(label="Exit", pos=(0,100))
		b.on_click=self.finish
		self.add_widget("button2", b)

		b=sgc.Button(label="Repair Hull", pos=(0,200))
		b.on_click=self.repair_hull
		self.add_widget("repairb", b)

		b=sgc.Button(label="Repair Systems", pos=(0,300))
		b.on_click=self.repair_systems
		self.add_widget("repairbs", b)

	def internal_update(self):		
		self.root.screen.screen.blit(self.root.gamedb(self.params["bg_image"]), (0,0))
		sgc.update(self.root.clock.get_fps())

		self.root.fps=9999

	def process_events(self, events):
		for event in events:
			sgc.event(event)