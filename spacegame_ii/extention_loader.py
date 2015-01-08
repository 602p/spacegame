import os, item, ship, serialize, primitives, imp, json, fnmatch, pygame, time
from logging import debug, info, warning, error, critical

def load_all_packages(root, dirn, console=None):
	root.extentions={}
	info("Loading Plugins")
	if console: post_and_flip(console, "VVV   Loading Plugins   VVV", bold=1, color=(0,255,0))
	load_plugins(root, dirn, console)
	info("Loading Assetkeys")
	if console: post_and_flip(console, "VVV   Loading Assets    VVV", bold=1, color=(0,255,0))
	load_assetkeys(root, dirn, console)
	info("Loading items")
	if console: post_and_flip(console, "VVV   Compiling Items   VVV", bold=1, color=(0,255,0))
	load_items(root, dirn, console)
	info("Loading Ships")
	if console: post_and_flip(console, "VVV   Compiling Ships   VVV", bold=1, color=(0,255,0))
	load_ships(root, dirn, console)
	if console:
		post_and_flip(console, "LOADING FINISHED!", bold=1, italic=1, color=(0,255,0))
		post_and_flip(console, "Loaded "+str(len(root.gamedb.assets))+" assets")
		post_and_flip(console, "Loaded "+str(len(root.item_factories))+" items")
		post_and_flip(console, "Loaded "+str(len(root.ship_factories))+" ships")
		time.sleep(2.5)

def findall(dirn, pattern):
	matches=[]
	for root, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, pattern):
			matches.append(os.path.join(root, filename))
	return sorted(matches)

def load_assetkeys(root, dirn, console):
	for rootn, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, "*.assetkey"):
			if console: post_and_flip(console, "Loading Assetkey '"+os.path.join(rootn, filename)+"'...", color=(255,255,255))
			root.gamedb.load_assetfile(os.path.join(rootn, filename), rootn.split("\\")[0]+"\\"+rootn.split("\\")[1]+"\\", console)

def load_plugins(root, dirn, console):
	for rn in findall(dirn, "*.plugin.py"):
		if console: post_and_flip(console, "Loading Plugin '"+rn+"'...", color=(255,255,255))
		load_plugin(root, rn, console)

def load_items(root, dirn, console):
	for rn in findall(dirn, "*.item"):
		if console: post_and_flip(console, "Loading Item '"+rn+"'...", color=(255,255,255))
		item.load_file(root, rn)

def load_ships(root, dirn, console):
	for rn in findall(dirn, "*.ship"):
		if console: post_and_flip(console, "Loading Ship '"+rn+"'...", color=(255,255,255))
		ship.load_file(root, rn)		

def load_plugin(root, fname, console):
	if not ".PYC" in fname.upper():
		debug("Load plugin '"+fname+"'")
		module_temp = imp.load_source('dynamicly_loaded_extention', fname)
		for funcname in dir(module_temp):
			if funcname.upper().startswith("INIT"):
				debug("Run init '"+fname+"'::"+funcname)
				if console: post_and_flip(console, "Initilizing Plugin '"+fname+"::"+funcname+"'...", color=(255,255,255))
				if eval("module_temp."+funcname+"(root)")==False:
					warning( "Loading of '"+funcname+"' from '"+fname+"' in '"+dirn+"' failed: False")

def post_and_flip(console, *args, **kwargs):
	console.post(*args, **kwargs)
	console.render((0,0))
	pygame.event.get()
	pygame.display.flip()
	#time.sleep(0.005)

class HookableExtention:
	def event_root(self, event):
		pass

	def event_state(self, state, event):
		pass