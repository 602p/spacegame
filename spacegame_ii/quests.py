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

class QuestFactory:
	def __init__(self, config):
		self.id=config["id"]
		self.name=dget(config, "name", "EVENT NAME")
		self.can_be_random=dget(config, "spawn_random", True)
		self.rarity=

class Quest:
	def __init__(self):
		pass

	def get_insert_dict(self):
		return {}

"""
QuestManager keeps track of your quests and each 5 (?) seconds checks to see if you have completed it.
It also instanciates and manages quests. It is also used to spawn random quests.

A Quest has some requirements needed to spawn it and a rarity. It also has events that are run right when it starts.
"""