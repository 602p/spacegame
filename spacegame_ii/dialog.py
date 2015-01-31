import json, primitives, random, state, pygame
from logging import debug, info, warning, error, critical

def init(root):
	root.dialog_manager=DialogManager(root)

def load_file(root, fname):
	debug("Load talk_file '"+fname)
	with open(fname, 'r') as f:
		root.dialog_manager.add_speech_config(json.load(f))

class DialogManager(object):
	def __init__(self, root):
		self.root=root
		self.other_ship=None
		self.pools={}

	def add_speech(self, speech):
		for pool in speech.pools:
			if pool not in self.pools.keys():
				self.pools[pool]=SpeechPool(self, pool)
			self.pools[pool].add_speech(speech)

	def add_speech_config(self, config):
		self.add_speech(Speech(self.root, config))

	def start_dialog(self, target, topic="greeting"):
		self.player=self.root.state_manager.states["game"].player
		self.other_ship=target
		self.root.state_manager.start_interdicting("dialog")

class SpeechPool(object):
	def __init__(self, manager, name):
		self.manager=manager
		self.root=manager.root
		self.pool={}
		self.name=name
		debug("Created pool:"+name)

	def add_speech(self, speech):
		if speech.priority not in self.pool.keys():
			self.pool[speech.priority]=[]
		debug("Added speech to pool:"+self.name)
		self.pool[speech.priority].append(speech)

	def get_for(self, name):
		updated_pool={}
		for key in self.pool.keys():
			for speech in self.pool[key]:
				if speech.is_valid():
					updated_pool[key].append(speech)
		sorted_pool=sorted(updated_pool)
		return random.sample(updated_pool[sorted_pool[0]], 1)

class Speech(object):
	def __init__(self, root, config):
		self.root=root
		self.text=config["text"]
		self.pools=config.get("keys",[])
		self.pools.append("_all")
		if "id" in config.keys():
			self.pools.append(config["id"])
		self.events=config.get("events",[])
		self.requirements=config.get("requirements",[])
		self.priority=config.get("priority",0)
		debug("Loaded speech (tags:"+str(self.pools)+")")

	def is_valid(self):
		return primitives.do_group_for_dialog(self.root, self.requirements, self.root.dialog_manager, self)

	def run_events(self):
		primitives.do_group_for_dialog(self.root, self.events, self.root.dialog_manager, self)

	def get_text(self):
		return self.text

class DialogState(state.InterdictingState):
	def first_start(self):
		debug("Starting dialog state...")
		self.dialog_manager=self.root.dialog_manager
		config=self.root.gamedb("cfg_dialog_box")
		self.config=config

		self.words_rect=pygame.Rect(*config["words_area"])
		self.goodbye_rect=pygame.Rect(*config["exit_button"])
		self.topics_rect=pygame.Rect(*config["topic_area"])

	def internal_update(self):
		screen=self.root.screen.screen
		config=self.root.gamedb("cfg_dialog_box")
		
		box_surf=self.root.gamedb("uia_dialog_box").copy()

		pygame.draw.rect(box_surf, (0,255,0), self.words_rect, 3)
		pygame.draw.rect(box_surf, (255,0,0), self.goodbye_rect, 3)
		pygame.draw.rect(box_surf, (0,0,255), self.topics_rect, 3)

		screen.blit(box_surf, config["box_pos"])

	def process_events(self, events):
		for event in events:
			if event.type==pygame.MOUSEBUTTONUP:
				if self.goodbye_rect.collidepoint((pygame.mouse.get_pos()[0]-self.config["box_pos"][0],pygame.mouse.get_pos()[1]-self.config["box_pos"][1])):
					self.finish()
