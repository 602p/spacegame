import state, sgc, pygame, uidict, serialize, textwrap
from logging import debug, info, warning, error, critical
import os
import sys,random,pygame,uidict,sgc

from pygame.locals import *
from sgc.locals import *

from toolbox import EasyGame

def init(root):
	root.widget_constructors={
		"Button":sgc.Button,
		"HBox":CompoundWidgetWrapper(sgc.HBox),
		"VBox":CompoundWidgetWrapper(sgc.VBox),
		"Label":sgc.Label,
		"Switch":sgc.Switch,
		"InputBox":sgc.InputBox,
		"Container":sgc.Container,
		"Combo":sgc.Combo
	}
	root.widget_controllers={
		"exit_state":ExitStateWidgetController,
		"json_settings_get":JSONSettingsBindingsGet,
		"json_settings_set":JSONSettingsBindingsSet,
		"call_state_callback":CallbackCaller,
		"popup_ok":PopupInterdictorController,
		"click_on_keypress":DoClickEventOnKeypress,
		"goto_binder":GotoBinderState,
		"yn_popup_quit":YNQuitter,
		"goto_ui_state":GotoUIState,
		"goto_state":GotoOtherState,
		"load_game":RunLoadGame,
		"save_game":RunSaveGame,
		"goto_istate":GotoOtherIState
	}

def interdict_ok(root, title="NOT_SET", text="NOT_SET", button="NOT_SET", callback=lambda s:0, wrap=48, key="sgcui_modalok"):
	debug("Calling UI_STATES::INTERDICT_OK...")
	debug("title="+title)
	debug("text="+text)
	debug("button="+button)
	debug("wrap="+str(wrap))
	debug("style="+key)
	text_=textwrap.wrap(text, wrap)
	text=""
	for l in text_:
		text+="\n"+l.replace("%n", "\n")
	state=root.state_manager.start_interdicting("generic_ui", root.gamedb(key))
	#print state.widgets.keys()
	state.widgets["replace_title"].config(text=title)
	state.widgets["replace_body"].config(text=text)
	state.widgets["replace_button"].config(label=button)
	state.callback=callback

def interdict_ok_node(root, config, callback=lambda s:0):
	if "body" in config.keys() and "text" not in config.keys():
		config["text"]=config["body"]
	interdict_ok(
		root,
		config.get("title","UNSET (interdict_ok_node)"),
		config.get("text","UNSET (interdict_ok_node)"),
		config.get("button","UNSET (interdict_ok_node)"),
		callback,
		config.get("wrap",48),
		config.get("key","sgcui_modalok")
	)

def interdict_yn(root, title="NOT_SET", text="NOT_SET", button_y="NOT_SET", button_n="NOT_SET",callback_y=lambda s:0, callback_n=lambda s:0, wrap=48, key="sgcui_modalyn"):
	debug("Calling UI_STATES::INTERDICT_YN...")
	debug("title="+title)
	debug("text="+text)
	debug("button_y="+button_y)
	debug("button_n="+button_n)
	debug("wrap="+str(wrap))
	debug("style="+key)
	text_=textwrap.wrap(text, wrap)
	text=""
	for l in text_:
		text+="\n"+l.replace("%n", "\n")
	state=root.state_manager.start_interdicting("generic_ui", root.gamedb(key))
	state.widgets["replace_title"].config(text=title)
	state.widgets["replace_body"].config(text=text)
	state.widgets["replace_button_yes"].config(label=button_y)
	state.widgets["replace_button_no"].config(label=button_n)
	state.callback_y=callback_y
	state.callback_n=callback_n
	return state

# Each widget gets a controller that has some bindings thru a binding layer to some number of components
# Each component is a stateful object and has hooks for on_click etc
# Components get references to root, GenericUIInterdictor, and it's bound widget.

class CompoundWidgetWrapper:
	def __init__(self, type_, key_in="widgets", key_out="widgets"):
		self.type_=type_
		self.key_in=key_in
		self.key_out=key_out

	def __call__(self, *args, **kwargs):
		widgets_list=kwargs[self.key_in]
		widget_objs=[]
		for widget in widgets_list:
			widget_objs.append(kwargs["__interdictor"].create_widget(widget, True, False, True))
		kwargs[self.key_out]=widget_objs
		return self.type_(*args, **kwargs)

class WidgetController:
	def __init__(self, config):
		self.config=config

	def bind(self, interface):
		self.interface=interface
		self.root=interface.root
		self.widget=interface.widget
		self.state=interface.state

	def on_click(self):
		pass

	def on_enter(self):
		pass

	def on_switch(self):
		pass

	def on_tick(self):
		pass

	def on_start(self):
		pass

	def on_event(self, e):
		pass

class ExitStateWidgetController(WidgetController):
	def on_click(self):
		self.interface.state.finish(self.config.get("value", None))

class JSONSettingsBindingsSet(WidgetController):
	def on_click(self):
		wrapper=uidict.UIDict(self.interface.root.settings)
		for key_id in self.config["bindings"].keys():
			if type(wrapper[self.config["bindings"][key_id]]) == bool:
				wrapper[self.config["bindings"][key_id]]=self.interface.state.widgets[key_id].state
			if type(wrapper[self.config["bindings"][key_id]]) == int:
				wrapper[self.config["bindings"][key_id]]=int(self.interface.state.widgets[key_id].text)
			if isinstance(wrapper[self.config["bindings"][key_id]],basestring):
				wrapper[self.config["bindings"][key_id]]=self.interface.state.widgets[key_id].text
		serialize.save_settings(self.interface.root.settings)

class JSONSettingsBindingsGet(WidgetController):
	def on_click(self):
		self.interface.root.settings=serialize.load_settings()
		wrapper=uidict.UIDict(self.interface.root.settings)
		for key_id in self.config["bindings"].keys():
			#print key_id
			if type(wrapper[self.config["bindings"][key_id]]) == bool:
				#print ":is bool"
				self.interface.state.widgets[key_id].config(state=wrapper[self.config["bindings"][key_id]])
			if type(wrapper[self.config["bindings"][key_id]]) == int:
				#print ":is int"
				self.interface.state.widgets[key_id].config(text=str(wrapper[self.config["bindings"][key_id]]), max_chars=999)
			if isinstance(wrapper[self.config["bindings"][key_id]],basestring):
				#print ":is string"
				self.interface.state.widgets[key_id].config(text=wrapper[self.config["bindings"][key_id]], max_chars=999)

	def on_start(self):
		self.on_click()

class CallbackCaller(WidgetController):
	def on_click(self):
		exec "self.state."+self.config["callback_name"]+"(self.state)"

class PopupInterdictorController(WidgetController):
	def _call(self):
		interdict_ok_node(self.root, self.config)

	def on_click(self): self._call()
	def on_enter(self): self._call()
	def on_switch(self): self._call()

class DoClickEventOnKeypress(WidgetController):
	def on_event(self, e):
		#print "e"
		if e.type==pygame.KEYDOWN:
			#print "k"
			if e.key==self.config.get("keycode", pygame.K_RETURN):
				#print "c"
				self.interface.state.widgets[self.config.get("widget_id", self.interface.widget._ui_id)].wai.on_click()

class GotoBinderState(WidgetController):
	def on_click(self):
		self.root.state_manager.start_interdicting("keymapper")

class YNQuitter(WidgetController):
	def on_click(self):
		interdict_yn(self.root, "Confirm", "Are you sure you want to quit?", "Don't Quit", "Quit", callback_n=lambda s:pygame.quit())

class GotoUIState(WidgetController):
	def on_click(self):
		self.root.state_manager.start_interdicting("generic_ui", self.root.gamedb(self.config["state_config"]))

class GotoOtherState(WidgetController):
	def on_click(self):
		self.root.state_manager.goto_state(self.config["state"])

class GotoOtherIState(WidgetController):
	def on_click(self):
		self.root.state_manager.start_interdicting(self.config["state"])

class RunLoadGame(WidgetController):
	def on_click(self):
		path = EasyGame.pathgetter("saves/", 1, "Select a savegame")
		serialize.load_game(self.root, path)
		#self.root.state_manager.goto_state("game")

class RunSaveGame(WidgetController):
	def on_click(self):
		path = EasyGame.pathgetter("saves/", 0, "Select a savegame")
		serialize.save_game(self.root, path)
		#self.root.state_manager.goto_state("game")

class WidgetAbstractionInterface:
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

	def on_start(self):
		for i in self.controllers:
			i.on_start()

	def on_event(self, e):
		for i in self.controllers:
			i.on_event(e)

class GenericUIInterdictor(state.InterdictingState):
	def del_widget(self, n):
		self.widgets[n].remove()
		del self.widgets[n]

	def get_widget(self, n):
		return self.widgets[n]

	def create_widget(self, config, add_dict=1, add_screen=1, _is_internal=0):
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
		config_["__interdictor"]=self

		if config_["type"] in self.root.widget_constructors.keys():
			#debug("Creating a '"+config_["type"]+"'")
			widget=self.root.widget_constructors[config_["type"]](**config_)
			widget._is_internal=_is_internal
			widget._json_config=config_
			widget.wai=WidgetAbstractionInterface(widget, self, self.root)
			for controller_cfg in config_.get("controllers",[]):
				if controller_cfg["controller"] in self.root.widget_controllers.keys():
					#debug("--Binding '"+controller_cfg["controller"]+"' to it")
					controller_obj=self.root.widget_controllers[controller_cfg["controller"]](controller_cfg)
					widget.wai.add_controller(controller_obj)
				else:
					error("--CONTROLLER "+controller_cfg["controller"]+" NOT FOUND!")
			if add_dict:
				key=config_.get("id", hash(widget))
				self.widgets[key]=widget
				widget._ui_id=key
			# if add_screen:
			# 	widget.add(order=config_.get("order",None))
			return widget
		else:
			error("WIDGET '"+config_["type"]+"' NOT FOUND")


	def construct_screen(self):
		info("Constructing screen...")
		self.default_config=self.params.get("defaults", {})
		self.bg_image=self.root.gamedb(self.params.get("bg_image", "large_black_bg"))
		for widget_cfg in self.params["widgets"]:
			self.create_widget(widget_cfg, 1, 0)

	def first_start(self):
		debug("Started a new ui state, creating widgets")
		self.widgets={}
		debug("Building new screen")
		self.construct_screen()

	def start(self):
		debug("ADDing widgets to screen")
		for i in self.widgets.keys():
			if not self.widgets[i]._is_internal: self.widgets[i].add(self.widgets[i]._json_config.get("order", None))
			self.widgets[i].wai.on_start()

	def internal_update(self):		
		if "bg_image" in self.params.keys():
			self.root.screen.screen.blit(self.root.gamedb(self.params["bg_image"]), (0,0))
		sgc.update(self.root.clock.get_fps())
		self.root.fps=9999

	def process_events(self, events):
		for event in events:
			sgc.event(event)
			for i in self.widgets.keys():
				self.widgets[i].wai.on_event(event)
				self.widgets[i].wai.on_tick()

	def clear_widgets(self):
		debug("removing widgets...")
		for i in self.widgets.keys():
			if not self.widgets[i]._is_internal: self.widgets[i].remove() #remove from screen, keep cached

	def suspend(self):
		debug("suspend() called, removing")
		self.clear_widgets()