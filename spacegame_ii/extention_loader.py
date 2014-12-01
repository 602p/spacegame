import os, item, ship, serialize, primitives, imp, json
from logging import debug, info, warning, error, critical

def load_all_packages(root, dirn):
	for i in os.listdir(dirn):
		load_package(root, dirn+"/"+i)

def load_package(root, dirn):
	debug("Load package '"+dirn+"'====================================================")
	flist=os.listdir(dirn)
	for fname in flist:
		if fname.upper()=="PLUGINS":
			load_plugins(root, dirn+"/"+fname)
	for fname in flist:
		if fname.upper()=="ASSETKEYS":
			for cfname in os.listdir(dirn+'/'+fname):
				debug("Load assetkey '"+dirn+"/"+fname+"/"+cfname+"'----")
				root.gamedb.load_assetfile(dirn+"/"+fname+"/"+cfname, dirn+'/')
	for fname in flist:
		if fname.upper()=="ITEMS":
			debug("Load item_dir '"+dirn+"/"+fname+"'")
			item.load_dir(root, dirn+"/"+fname)
	for fname in flist:
		if fname.upper()=="SHIPS":
			debug("Load ship_dir '"+dirn+"/"+fname+"'")
			ship.load_dir(root, dirn+"/"+fname)
		

def load_plugins(root, dirn):
	for fname in os.listdir(dirn):
		if not ".PYC" in fname.upper():
			debug("Load plugin '"+dirn+"/"+fname+"'")
			module_temp = imp.load_source('module', dirn+"/"+fname)
			for funcname in dir(module_temp):
				if funcname.upper().startswith("INIT"):
					debug("Run init '"+dirn+"/"+fname+"'::"+funcname)
					if eval("module_temp."+funcname+"(root)")==False:
						warning( "Loading of '"+funcname+"' from '"+fname+"' in '"+dirn+"' failed: False")
