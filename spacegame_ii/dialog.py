import json, primitives, random, state, pygame, textwrap, random, jsonutil, formatting
from logging import debug, info, warning, error, critical
import logging, assets, absroot
module_logger=logging.getLogger("sg.dialog")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	root.dialog_manager=DialogManager(root)

@assets.load_where_endswith(".talk")
def load_dialog(config, *a):
	absroot.dialog_manager.add_speech_config(jsonutil.get_expanded_json(absroot.gamedb, config))

class DialogManager(object):
	def __init__(self, root):
		self.root=root
		self.other_ship=None
		self.pools={}
		self.poolmappings={}
		self.current=None

	def init_each_game(self):
		self.known_topics=[]
		debug("init_each_game::Loading talkpools_*")
		for poolset in self.root.gamedb.get_startswith("talkpools_"):
			for config in poolset:
				#print config
				self.poolmappings[config["id"]]=config["name"]
				if config.get("kas", False):
					self.known_topics.append(config["id"])
					debug("Adding preknown dialog:"+config["id"])
		#print self.poolmappings

	def learn_topic(self, idx):
		if idx not in self.known_topics:
			self.known_topics.append(idx)

	def add_speech(self, speech):
		for pool in speech.pools:
			if pool not in self.pools.keys():
				self.pools[pool]=SpeechPool(self, pool)
			self.pools[pool].add_speech(speech)

	def add_speech_config(self, config):
		self.add_speech(Speech(self.root, config))

	def start_dialog(self, target, topic="greeting"):
		self.player=self.root.state_manager.states["game"].player
		self.othership=target
		self.current_state=self.root.state_manager.start_interdicting("dialog", [topic, self.player.get_faction_attr("dialog_font_group","font_dialog_default")])

	def get_for(self, name):
		s=self.pools[name].get_speech()
		s.run_events()
		return s

	def save_to_config_node(self):
		return {
			"pools":"LART",
			"known_topics":self.known_topics
		}

	def do_additional_load(self, config):
		for topic in config["known_topics"]: self.learn_topic(topic)

	def count_speeches(self):
		c=0
		for pool in self.pools.keys():
			c+=self.pools[pool].count_speeches()
		return c

	def count_pools(self):
		return len(self.pools.keys())

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

	def count_speeches(self):
		c=0
		for pri in self.pool.keys():
			c+=len(self.pool[pri])
		return c

	def get_speech(self):
		#random.seed(self.root.game_time*82)
		updated_pool={}
		for key in self.pool.keys():
			for speech in self.pool[key]:
				if speech.is_valid():
					if key not in updated_pool.keys():
						updated_pool[key]=[]
					updated_pool[key].append(speech)
		sorted_pool=sorted(updated_pool)
		sorted_pool.reverse()
		# print sorted_pool
		# print updated_pool
		return random.sample(updated_pool[sorted_pool[0]], 1)[0]

class Speech(object):
	def __init__(self, root, config, x_bold=0):
		self.root=root
		self.bold=x_bold
		self.text=config["text"].replace("\\n","\n").replace("%n","\n")
		self.pools=config.get("keys",[])
		self.pools.append("_all")
		if "id" in config.keys():
			self.pools.append(config["id"])
		self.events=config.get("events",[])
		self.requirements=config.get("requirements",[])
		self.priority=config.get("priority",0)
		debug("Loaded speech (tags:"+str(self.pools)+")")

	def is_valid(self):
		v=primitives.do_group_for_dialog(self.root, self.requirements, self.root.dialog_manager, self)
		debug("Checking ?"+self.pools[0])
		debug("Got "+str(v))
		return v

	def run_events(self):
		primitives.do_group_for_dialog(self.root, self.events, self.root.dialog_manager, self)

	def get_text(self):
		return self.text

def _create_speech(root, text, x_bold=0):
	return Speech(root, {"text":text}, x_bold)

class DialogState(state.InterdictingState):
	def first_start(self):
		debug("Starting dialog state...")

		self.dialog_manager=self.root.dialog_manager
		self.dialog_manager.current=self
		config=self.root.gamedb("cfg_dialog_box")
		self.config=config
		self.othership=self.dialog_manager.othership

		self.screenshot=self.root.screen.screen.copy().convert_alpha()
		self.screenshot.subsurface(pygame.Rect(config["box_pos"], self.root.gamedb("uia_dialog_box").get_size()))\
		 .fill(pygame.Color(0,0,0,0))

		self.words_rect=pygame.Rect(*config["words_area"])
		self.goodbye_rect=pygame.Rect(*config["exit_button"])
		self.topics_rect=pygame.Rect(*config["topic_area"])
		self.box_pos=config["box_pos"]
		self.rep_pos=pygame.Rect(config["relations_pos"], (999, 999))

		self.words_rect.move_ip(self.box_pos)
		self.goodbye_rect.move_ip(self.box_pos)
		self.topics_rect.move_ip(self.box_pos)
		self.rep_pos.move_ip(self.box_pos)
		
		self.font=self.root.gamedb(self.params[1]+".text")
		self.titlefont=self.root.gamedb("font_inventory_large")
		self.topic_font=self.root.gamedb(self.params[1]+".topic")
		self.max_width=int(self.words_rect.width/self.font.size("_")[0])-2
		
		self.text_scroll=0
		self.topics_scroll=0
		self.can_exit=True

		self.has_init=0

	def show_loading(self):
		size=self.root.gamedb("font_standard_large").size("LOADING...")
		pos=[(self.root.gamedb("uia_dialog_box").get_size()[0]/2)-(size[0]/2), (self.root.gamedb("uia_dialog_box").get_size()[1]/2)-(size[1]/2)]
		pos[0]+=self.box_pos[0]
		pos[1]+=self.box_pos[1]

		pygame.draw.rect(self.root.screen.screen, (0,0,0), pygame.Rect(pos, size) )
		self.root.screen.screen.blit(self.root.gamedb("font_standard_large").render("LOADING...", 1, (255,0,0)), pos)

	def rebuild_text(self):
		self.show_loading()
		pygame.display.flip()
		self.hotspots=[]
		self.text_image=pygame.Surface((self.words_rect.width, 10000)).convert_alpha()
		self.text_image.fill(pygame.Color(0,0,0,0))
		current_pos=[0,0]
		#print current_pos
		debug("Rebuilding dialog text")
		need_trb=False

		for speech in self.speeches:
			if speech.text:
				split_text=[]
				tmp_text=speech.text.replace("\r","")
				rep_text=formatting.SubFormatter(self.root.formatter,{
					"dialog_s":self,
					"dialog_m":self.dialog_manager,
					"speech":speech,
					"othership":self.dialog_manager.othership,
					"player":self.root.state_manager.states["game"].player,
					"savedb":self.root.savegame.database
				}).format_string(tmp_text)
				for line in rep_text.split("\n"):
					split_text.append(line.replace("\n",""))

				for line in split_text:
					for token in line.split(" "):
						if token!="":
							if current_pos[0]+self.font.size(token+" ")[0]>self.words_rect.width:
								current_pos[0]=0
								current_pos[1]+=self.font.size("|")[1]
							if token.startswith("$@") and token.endswith("@$"):
								self.font.set_bold(1)
								token, speech_pointer = token.replace("@$","").replace("$@","").split(":")

								if speech_pointer in self.dialog_manager.poolmappings.keys():
									self.dialog_manager.learn_topic(speech_pointer)
									need_trb=True
								

								surf=pygame.Surface(self.font.size(token)).convert_alpha()
								surf.fill((255,0,0,220))
								self.text_image.blit(surf, current_pos)
								self.hotspots.append([pygame.Rect(current_pos, surf.get_size()),speech_pointer,token])
							else:
								self.font.set_bold(0)
							self.text_image.blit(self.font.render(token, 1, (255,255,255)), current_pos)
							current_pos[0]+=self.font.size(token+" ")[0]
							

					current_pos[1]+=self.font.size("|")[1]
					current_pos[0]=0

		new_surf=pygame.Surface((self.text_image.get_bounding_rect().width+100,
			self.text_image.get_bounding_rect().height+50)).convert_alpha()
		new_surf.fill(pygame.Color(0,0,0,0))
		new_surf.blit(self.text_image, (0,0))
		self.text_image=new_surf
		if need_trb:
			self.rebuild_topics()

	def rebuild_topics(self):
		self.show_loading()
		pygame.display.flip()
		debug("Rebuilding topics")
		self.topic_font.set_bold(1)
		self.topics_hotspots=[]
		preadj_surf=pygame.Surface((self.topics_rect.width,10000)).convert_alpha()
		preadj_surf.fill(pygame.Color(0,0,0,0))
		current_pos=[0,0]

		for topic in self.dialog_manager.known_topics:
			topic_text=self.dialog_manager.poolmappings[topic]
			preadj_surf.blit(self.topic_font.render(topic_text, 1, (255,255,255)), current_pos)
			#print topic+" :: "+topic_text

			surf=pygame.Surface(self.topic_font.size(topic_text)).convert_alpha()
			# surf.fill((255,0,0,180))
			# preadj_surf.blit(surf, current_pos)
			self.topics_hotspots.append([pygame.Rect(current_pos, surf.get_size()), topic, topic_text])

			current_pos[1]+=self.topic_font.size("|")[1]
			current_pos[0]=0

		self.topic_font.set_bold(0)
		new_surf=pygame.Surface((preadj_surf.get_bounding_rect().width+100,
		 preadj_surf.get_bounding_rect().height+50)).convert_alpha()
		new_surf.fill(pygame.Color(0,0,0,0))
		new_surf.blit(preadj_surf, (0,0))
		self.topics_image=new_surf

	def internal_update(self):
		if not self.has_init:
			self.speeches=[self.dialog_manager.get_for(self.params[0])]
			debug("Selected first speech as ?"+self.speeches[0].pools[0])
			self.rebuild_text()
			self.rebuild_topics()
			self.has_init=1
		screen=self.root.screen.screen
		config=self.root.gamedb("cfg_dialog_box")
		
		screen.blit(self.root.gamedb("uia_dialog_box"), self.box_pos)

		#pygame.draw.rect(screen, (0,255,0), self.words_rect, 3)
		pygame.draw.rect(screen, (255,0,0), self.goodbye_rect, 3)
		pygame.draw.rect(screen, (0,0,255), self.topics_rect, 3)

		if not self.can_exit:
			pygame.draw.rect(screen, (255,0,0), self.goodbye_rect, 0)

		screen.blit(self.text_image, (self.words_rect.left, self.words_rect.top-self.text_scroll))
		screen.blit(self.topics_image, (self.topics_rect.left, self.topics_rect.top-self.topics_scroll))
		screen.blit(self.font.render("Reputation: "+str(self.dialog_manager.othership.player_relations), 1, (255,255,255)), self.rep_pos)
		screen.blit(self.screenshot, (0,0))
		screen.blit(self.font.render("OSHIP_:"+self.othership.name, 1, (255,255,255)), (0,0))
		screen.blit(self.titlefont.render("Hailing "+self.dialog_manager.othership.name, 1, self.dialog_manager.othership.get_faction_attr("color", (255,255,255))), (self.box_pos[0], self.box_pos[1]-self.titlefont.size("|")[1]))


	def process_events(self, events):
		for event in events:
			if event.type==pygame.MOUSEBUTTONUP:
				if event.button==1:
					if self.goodbye_rect.collidepoint(pygame.mouse.get_pos()):
						if self.can_exit:
							self.finish()
					for rect, pointer, text in self.hotspots:
						if rect.collidepoint((pygame.mouse.get_pos()[0]-self.box_pos[0], pygame.mouse.get_pos()[1]-self.box_pos[1]+self.text_scroll)):
							self.speeches.append(_create_speech(self.root, " "))
							self.speeches.append(_create_speech(self.root, "/-----"+text+('-'*(self.max_width-5-len(text)-1))+"\\", 1))

							self.speeches.append(self.dialog_manager.get_for(pointer))
							self.speeches.append(_create_speech(self.root, "\\"+'-'*(self.max_width-1)+"/", 1))

							self.rebuild_text()
					for rect, pointer, text in self.topics_hotspots:
						if rect.collidepoint((pygame.mouse.get_pos()[0]-self.topics_rect.left, pygame.mouse.get_pos()[1]+self.topics_scroll-self.topics_rect.top)):
							self.speeches.append(_create_speech(self.root, " "))
							self.speeches.append(_create_speech(self.root, "/-----"+text+('-'*(self.max_width-5-len(text)-1))+"\\", 1))

							self.speeches.append(self.dialog_manager.get_for(pointer))
							self.speeches.append(_create_speech(self.root, "\\"+'-'*(self.max_width-1)+"/", 1))

							self.rebuild_text()
			if event.type==pygame.MOUSEBUTTONDOWN:
				if self.words_rect.collidepoint(pygame.mouse.get_pos()):
					if event.button==5:
						self.text_scroll+=15
					if event.button==4:
						self.text_scroll-=15
				elif self.topics_rect.collidepoint(pygame.mouse.get_pos()):
					if event.button==5:
						self.topics_scroll+=15
					if event.button==4:
						self.topics_scroll-=15