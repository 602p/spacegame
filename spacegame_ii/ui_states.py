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

import sgc
from sgc.locals import *


# Each widget gets a controller that has some bindings thru a binding layer to some number of components
# Each component is a stateful object and has hooks for on_click etc
# Components get references to root, GenericUIInterdictor, and it's bound widget.

class CompoundWidgetWrapper:
	def __init__(self, type_, interdictor, key_in="widgets", key_out="widgets"):
		self.type_=type_
		self.key_in=key_in
		self.key_out=key_out
		self.interdictor=interdictor

	def __call__(self, *args, **kwargs):
		widgets_list=kwargs[self.key_in]
		widget_objs=[]
		for widget in widgets_list:
			widget_objs.append(self.interdictor.create_widget(widget, False))
		kwargs[self.key_out]=widget_objs
		return self.type_(*args, **kwargs)

class WidgetController:
	def __init__(self, config):
		self.config=config

	def bind(self, interface):
		self.interface=interface

	def on_click(self):
		pass

	def on_enter(self):
		pass

	def on_switch(self):
		pass

	def on_tick(self):
		pass

class ExitStateWidgetController(WidgetController):
	def on_click(self):
		self.interface.state.finish(self.config.get("value", None))

class WidgetInterfaceAbstractor:
	def __init__(self, widget, state, root):
		self.widget=widget
		self.state=state
		self.root=root
		self.controllers=[]

		widget.on_click=self.on_click
		widget.on_enter=self.on_enter
		widget.on_switch=self.on_switch

	def add_controller(self, controller):
		self.controllers.append(controller)
		controller.bind(self)

	def on_click(self):
		for i in self.controllers:
			i.on_click()

	def on_enter(self):
		for i in self.controllers:
			i.on_enter()

	def on_switch(self):
		for i in self.controllers:
			i.on_switch()

	def on_tick(self):
		for i in self.controllers:
			i.on_tick()

class GenericUIInterdictor(state.InterdictingState):
	def add_widget(self, n, w):
		self.widgets[n]=w
		self.widgets[n].add()

	def del_widget(self, n):
		self.widgets[n].remove()
		del self.widgets[n]

	def get_widget(self, n):
		return self.widgets[n]

	def create_widget(self, config, add=1):
		config_=self.default_config.copy()
		config_.update(config)

		def process_inserts(node, db):
			for i in node.keys():
				if isinstance(node[i], basestring):
					if node[i].startswith("$"):
						node[i]=db(node[i].replace("$",""))
				if isinstance(node[i], dict):
					node[i]=process_inserts(node[i], db)
			return node

		config_=process_inserts(config, self.root.gamedb)

		if config_["type"] in self.widget_constructors.keys():
			debug("Creating a '"+config_["type"]+"'")
			widget=self.widget_constructors[config_["type"]](**config_)
			widget.wai=WidgetInterfaceAbstractor(widget, self, self.root)
			for controller_cfg in config_.get("controllers",[]):
				if controller_cfg["controller"] in self.widget_controllers.keys():
					debug("--Binding '"+controller_cfg["controller"]+"' to it")
					controller_obj=self.widget_controllers[controller_cfg["controller"]](controller_cfg)
					widget.wai.add_controller(controller_obj)
				else:
					error("--CONTROLLER "+controller_cfg["controller"]+" NOT FOUND!")
			if add:
				if "id" in config_:
					self.add_widget(config_["id"], widget)
				else:
					self.add_widget(hash(widget), widget)
			return widget
		else:
			error("WIDGET '"+config_["type"]+"' NOT FOUND")


	def construct_screen(self):
		info("Constructing screen...")
		self.default_config=self.params.get("defaults", {})
		self.bg_image=self.root.gamedb(self.params.get("bg_image", "large_black_bg"))
		for widget_cfg in self.params["widgets"]:
			self.create_widget(widget_cfg)

	def first_start(self):
		self.widget_constructors={
			"Button":sgc.Button,
			"HBox":CompoundWidgetWrapper(sgc.HBox, self),
			"VBox":CompoundWidgetWrapper(sgc.VBox, self),
			"Label":sgc.Label,
			"Switch":sgc.Switch,
			"InputBox":sgc.InputBox
		}
		self.widget_controllers={
			"exit_state":ExitStateWidgetController
		}
		self.widgets={}

	def start(self):
		self.clear_widgets()
		self.construct_screen()

	def internal_update(self):		
		self.root.screen.screen.blit(self.root.gamedb(self.params["bg_image"]), (0,0))
		sgc.update(self.root.clock.get_fps())
		for i in self.widgets.keys():
			self.widgets[i].wai.on_tick()
		self.root.fps=9999

	def process_events(self, events):
		for event in events:
			sgc.event(event)

	def clear_widgets(self):
		for i in self.widgets.keys():
			self.del_widget(i)

	def suspend(self):
		self.clear_widgets()