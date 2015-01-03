import random
from jsonutil import dget

def init(root):
	if not 'item_factories' in dir(root):
		root.item_factories={}

def load_dir(root, dname):
	for i in os.listdir(dname):
		load_file(root, dname+"/"+i, dname)

def load_file(root, fname, package_root):
	debug("Load item_file '"+fname+"' from '"+package_root+"'")
	with open(fname, 'r') as f:
		load_string(root, f.read(), package_root)

def load_string(root, string, package_root):
	register_item(root, get_expanded_json(root.gamedb, json.loads(string)), package_root)

def register_item(root, config, package_root):
	root.item_factories[config["id"]]=create_item_factory(root, config, package_root)

def create_item_factory(root, config, package_root):
	return ItemFactory(root, package_root, config)

def create_item(root, name, parent, equipped=-1):
	return root.item_factories[name](parent, equipped)

class RandomFactory:
	def __init__(self, config):
		self.id=config["id"]
		self.name=dget(config, "name", "EVENT NAME")
		self.can_be_random=dget(config, "spawn_random", True)
		self.