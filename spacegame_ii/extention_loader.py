import os, item, ship, serialize, primitives, imp, json, fnmatch
from logging import debug, info, warning, error, critical

def load_all_packages(root, dirn):
	info("Loading Plugins")
	load_plugins(root, dirn)
	info("Loading Assetkeys")
	load_assetkeys(root, dirn)
	info("Loading items")
	load_items(root, dirn)
	info("Loading Ships")
	load_ships(root, dirn)

def findall(dirn, pattern):
	matches=[]
	for root, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, pattern):
			matches.append(os.path.join(root, filename))
	return sorted(matches)

def load_assetkeys(root, dirn):
	for rootn, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, "*.assetkey"):
			root.gamedb.load_assetfile(os.path.join(rootn, filename), rootn.split("\\")[0]+"\\"+rootn.split("\\")[1]+"\\")

def load_plugins(root, dirn):
	for rn in findall(dirn, "*.plugin.py"):
		load_plugin(root, rn)

def load_items(root, dirn):
	for rn in findall(dirn, "*.item"):
		item.load_file(root, rn)

def load_items(root, dirn):
	for rn in findall(dirn, "*.item"):
		item.load_file(root, rn)

def load_ships(root, dirn):
	for rn in findall(dirn, "*.ship"):
		ship.load_file(root, rn)		

def load_plugin(root, fname):
	if not ".PYC" in fname.upper():
		debug("Load plugin '"+fname+"'")
		module_temp = imp.load_source('dynamicly_loaded_extention', fname)
		for funcname in dir(module_temp):
			if funcname.upper().startswith("INIT"):
				debug("Run init '"+fname+"'::"+funcname)
				if eval("module_temp."+funcname+"(root)")==False:
					warning( "Loading of '"+funcname+"' from '"+fname+"' in '"+dirn+"' failed: False")