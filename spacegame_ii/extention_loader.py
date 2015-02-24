import os, item, ship, serialize, primitives, imp, json, fnmatch, pygame, time, sys, dialog, quests, faction
from logging import debug, info, warning, error, critical

def load_all_packages(root, dirn, console=None):
	info("Loading Plugins")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Loading Plugins   V V V", bold=1, color=(0,255,0))
	load_plugins(root, dirn, console)
	info("Doing last plugin init...")
	for ext in root.extentions:
		root.extentions[ext].after_plugins_load()
	info("Loading Assetkeys")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Loading Assets    V V V", bold=1, color=(0,255,0))
	load_assetkeys(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_assets_load()
	info("Loading items")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Compiling Items   V V V", bold=1, color=(0,255,0))
	load_items(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_items_load()
	info("Loading Ships")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Compiling Ships   V V V", bold=1, color=(0,255,0))
	load_ships(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_ships_load()

	info("Loading dialog")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V  Installing Dialog  V V V", bold=1, color=(0,255,0))
	load_dialog(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_dialog_load()

	info("Loading factions")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V Installing Factions V V V", bold=1, color=(0,255,0))
	load_factions(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_faction_load()

	info("Loading quests")
	if console: post_and_flip(console, "V V V  Compiling  Quests  V V V", bold=1, color=(0,255,0))
	load_quests(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_quests_load()

	if console:
		post_and_flip(console, "LOADING FINISHED!", bold=1, italic=1, color=(0,255,0))
		post_and_flip(console, "Loaded "+str(len(root.gamedb.assets))+" assets")
		post_and_flip(console, "Loaded "+str(len(root.item_factories))+" items")
		post_and_flip(console, "Loaded "+str(len(root.ship_factories))+" ships")
		post_and_flip(console, "Loaded "+str(root.dialog_manager.count_pools())+" speech pools ("+str(root.dialog_manager.count_speeches())+" speechis distributed)")
		post_and_flip(console, "Loaded "+str(len(root.quest_factories))+" quests")
		post_and_flip(console, "(Sectors get loaded at runtime C: )")
		time.sleep(2.5)

def safepost(console, text, bold=0, italic=0, underline=0, color=(255,255,255), bg=(0,0,0), debugmsg=False):
	if console:
		post_and_flip(console, text, bold=bold, italic=italic, underline=underline, color=color, bg=bg, debugmsg=debugmsg)

def findall(dirn, pattern):
	matches=[]
	for root, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, pattern):
			matches.append(os.path.join(root, filename))
	return sorted(matches)

def load_assetkeys(root, dirn, console):
	for rootn, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, "*.assetkey"):
			root.gamedb.load_assetfile(os.path.join(rootn, filename), rootn.split("\\")[0]+"\\"+rootn.split("\\")[1]+"\\", console)
	root.gamedb.process_delayed_load(console)

def load_plugins(root, dirn, console):
	for rn in findall(dirn, "*.plugin.py"):
		if console: post_and_flip(console, "Loading Plugin '"+rn+"'...", color=(255,255,255))
		load_plugin(root, rn, console)

def load_quests(root, dirn, console):
	for rn in findall(dirn, "*.quest"):
		if console: post_and_flip(console, "Loading Quest '"+rn+"'...", color=(255,255,255))
		quests.load_file(root, rn)

def load_items(root, dirn, console):
	for rn in findall(dirn, "*.item"):
		if console: post_and_flip(console, "Loading Item '"+rn+"'...", color=(255,255,255))
		item.load_file(root, rn)

def load_factions(root, dirn, console):
	for rn in findall(dirn, "*.faction"):
		if console: post_and_flip(console, "Loading Faction '"+rn+"'...", color=(255,255,255))
		faction.load_file(root, rn)

def load_dialog(root, dirn, console):
	for rn in findall(dirn, "*.talk"):
		if console: post_and_flip(console, "Loading dialog '"+rn+"'...", color=(255,255,255))
		dialog.load_file(root, rn)

def load_ships(root, dirn, console):
	for rn in findall(dirn, "*.ship"):
		if console: post_and_flip(console, "Loading Ship '"+rn+"'...", color=(255,255,255))
		ship.load_file(root, rn)	

def load_galaxy(root, dirn, console):
	import sectors #dumb hack to fix circular imports
	c=0
	for rn in findall(dirn, "*.sector"):
		c+=1
		if console: post_and_flip(console, "Loading Sector '"+rn+"'...", color=(255,255,255))
		sectors.load_file(root, rn)		
	return c

def load_plugin(root, fname, console):
	if not ".PYC" in fname.upper():
		debug("Load plugin '"+fname+"'")
		key=fname.replace("\\", "").replace(".", "")
		exec key+" = imp.load_source('"+key+"', fname)"
		for funcname in eval("dir("+key+")"):
			if funcname.upper().startswith("INIT"):
				debug("Run init '"+fname+"'::"+funcname)
				if console: post_and_flip(console, "Initilizing Plugin '"+fname+"::"+funcname+"'...", color=(255,255,255))
				if eval(key+"."+funcname+"(root, console)")==False:
					warning( "Loading of '"+funcname+"' from '"+fname+"' in '"+dirn+"' failed: False")

def post_and_flip(console, *args, **kwargs):
	console.post(*args, **kwargs)
	console.render((0,0))
	for i in pygame.event.get():
		if i.type==pygame.QUIT:
			sys.exit(1)
	pygame.display.flip()
	#time.sleep(0.005)

class HookableExtention(object):
	def __init__(self, root):
		self.root=root
		
	def event_root(self, event):
		pass

	def event_state(self, state, event):
		pass

	def last_load(self):
		pass

	def after_plugins_load(self):
		pass

	def after_assets_load(self):
		pass

	def after_items_load(self):
		pass

	def after_ships_load(self):
		pass

	def after_dialog_load(self):
		pass

	def after_quests_load(self):
		pass

	def after_faction_load(self):
		pass

	def tick(self, state):
		pass