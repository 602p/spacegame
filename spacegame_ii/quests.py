from __future__ import division
import random, rarity, primitives, json, absroot, state, tooltips
from logging import debug, info, warn, error, critical
from jsonutil import dget, get_expanded_json
import logging
module_logger=logging.getLogger("sg.quests")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def init(root):
	if not 'quest_factories' in dir(root):
		root.quest_factories={}

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i, dname)

def load_file(root, fname):
	debug("Load quest_file '"+fname)
	with open(fname, 'r') as f:
		load_string(root, f.read())

def load_string(root, string):
	register_quest(root, get_expanded_json(root.gamedb, json.loads(string)))

def register_quest(root, config):
	root.quest_factories[config["id"]]=create_quest_factory(root, config)

def create_quest_factory(root, config):
	return QuestFactory(root, config)

def create_quest(root, name):
	return root.quest_factories[name]()

class QuestManager(object):
	def __init__(self, root, player):
		self.player=player
		self.root=root
		self.quests=[]

	def sort_quests(self):
		self.quests.sort(key=lambda q:-q.sort_order)

	def update(self):
		for factory_id in self.root.quest_factories.keys():
			if self.root.quest_factories[factory_id].should_spawn():
				self.start_quest(factory_id)

	def start_quest(self, idx):
		self.add_quest(self.root.quest_factories[idx]())

	def add_quest(self, quest):
		self.quests.append(quest)
		quest.start()

	def save_to_config_node(self):
		qlist=[]
		for quest in self.quests:
			qlist.append(quest.save_to_config_node())
		return {
			"quests":qlist
		}

	def load_quests(self, config):
		for qdata in config["quests"]:
			self.quests.append(create_quest(self.root, qdata["id"]))
			self.quests[-1].do_additional_load(qdata)

	def get_quest_for_ship(self, hid):
		for quest in self.quests:
			for key in quest.database["ship_mappings"].keys():
				if quest.database["ship_mappings"][key]==hid:
					return quest

class QuestFactory(object):
	def __init__(self, root, config):
		self.id=config["id"]
		self.name=config.get("name", "EVENT NAME")
		self.can_be_random=config.get("spawn_random", True)
		self.rarity=rarity.Rarity(config.get("rarity", {}))
		self.spawn_requirements=config.get("spawn_requirements",[])
		
		self.config=config
		self.root=root

		self.last_spawn_check=root.game_time

	def can_spawn(self):
		if not self.can_be_random: return False
		return primitives.do_group_for_event(self.root, self.spawn_requirements, self)

	def get_spawn_chance(self):
		#print self.root.game_time-self.last_spawn_check
		a = self.rarity.should_happen(absroot.galaxy.get_sector().tags, self.root.game_time-self.last_spawn_check)
		self.last_spawn_check=self.root.game_time
		return a

	def should_spawn(self):
		return self.can_spawn() and self.get_spawn_chance()

	def __call__(self):
		return Quest(self.root, self.config)

class Quest(tooltips.GenericTooltipMixin):
	def __init__(self, root, config):
		self.config=config
		self.root=root
		self.sort_order=config.get("sort_order", 0)
		self.id=config["id"]
		self.name=config.get("name", "EVENT_NAME")
		self.tags=config.get("tags",[])
		self.intro=config.get("intro", self.name+" has started!")
		self.events=config.get("events", [])
		self.finish_events=config.get("finish_events", [])
		self.database={
			"ship_mappings":{}
		}
		self.state=0
		self.active=True

	def start(self):
		self.root.igconsole.post(self.intro, color=(255,255,0), italic=1)
		primitives.do_group_for_event(self.root, self.events, self)

	def finish(self):
		primitives.do_group_for_event(self.root, self.finish_events, self)
		self.active=False

	def save_to_config_node(self):
		return {
			"id":self.id,
			"database":self.database,
			"state":self.state,
			"active":self.active
		}

	def do_additional_load(self, config):
		self.database=config["database"]
		self.state=config["state"]
		self.active=config["active"]

	def get_descriptions(self):
		return "Not Implemented"

	def tt_render_image(self):
		self.tt_image_init((1000,1000))
		self.tt_image.blit(absroot.gamedb("font_item_title").render(self.name, 1, (200,200,200)), (0,0))
		self.tt_image.blit(
			tooltips.render_wrapped_text(self.get_description(), 400, absroot.gamedb("font_item_desc"), (40,40,40))
			,(0, absroot.gamedb("font_item_title").size("|")[1]))
		self.tt_image_clip()
		self.tt_add_box()