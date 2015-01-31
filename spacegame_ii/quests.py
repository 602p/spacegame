from __future__ import division
import random, rarity, primitives
from jsonutil import dget

def init(root):
	if not 'quest_factories' in dir(root):
		root.quest_factories={}

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i, dname)

def load_file(root, fname, package_root):
	debug("Load quest_file '"+fname+"' from '"+package_root+"'")
	with open(fname, 'r') as f:
		load_string(root, f.read(), package_root)

def load_string(root, string, package_root):
	register_quest(root, get_expanded_json(root.gamedb, json.loads(string)), package_root)

def register_quest(root, config, package_root):
	root.quest_factories[config["id"]]=create_quest_factory(root, config, package_root)

def create_quest_factory(root, config, package_root):
	return QuestFactory(root, package_root, config)

def create_quest(root, name, parent, equipped=-1):
	return root.quest_factories[name](parent, equipped)

class QuestManager:
	def __init__(self, root, player):
		self.player=player
		self.root=root
		self.quests=[]

	def sort_quests(self):
		self.quests.sort(key=lambda q:q.sort_order)

class QuestFactory:
	def __init__(self, config, root):
		self.id=config["id"]
		self.name=config.get("name", "EVENT NAME")
		self.can_be_random=config.get("spawn_random", True)
		self.rarity=rarity.Rarity(config.get("rarity", rarity.default_rarity))
		self.spawn_requirements=config.get("spawn_requirements",[])
		self.root=root

		self.last_spawn_check=root.game_time

	def can_spawn(self):
		return primitives.do_group_for_event(self.spawn_requirements, self)

	def get_spawn_chance(self):
		a = self.rarity.should_have("", self.root.game_time-self.last_spawn_check) #TODO: Setup when sectors have tags
		self.last_spawn_check=self.root.game_time
		return a

	def should_spawn(self):
		return self.can_spawn() and self.get_spawn_chance()

class Quest:
	def __init__(self, config):
		self.config=config
		self.sort_order=config.get("sort_order", 0)
		self.id=config["id"]
		self.name=config.get("name", "EVENT_NAME")
		self.tags=config.get("tags",[])

	

"""
QuestManager keeps track of your quests and each 5 (?) seconds checks to see if you have completed it.
It also instanciates and manages quests. It is also used to spawn random quests.

A Quest has some requirements needed to spawn it and a rarity. It also has events that are run right when it starts.
-name
-id
-rarity
-spawn requirements
-finish requirements
-sort order (highest at top)
"""