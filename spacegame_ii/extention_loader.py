import os, item, ship, serialize, primitives, imp, json

def load_all_packages(root, dirn):
	for i in os.listdir(dirn):
		load_package(root, dirn+"/"+i)

def load_package(root, dirn):
	flist=os.listdir(dirn)
	for fname in flist:
		if fname.upper()=="PLUGINS":
			load_plugins(root, dirn+"/"+fname)
	for fname in flist:
		if fname.upper()=="ASSETKEYS":
			for cfname in os.listdir(dirn+'/'+fname):
				root.gamedb.load_assetfile(dirn+"/"+fname+"/"+cfname, dirn+'/')
	for fname in flist:
		if fname.upper()=="ITEMS":
			item.load_dir(root, dirn+"/"+fname)
	for fname in flist:
		if fname.upper()=="SHIPS":
			ship.load_dir(root, dirn+"/"+fname)
		

def load_plugins(root, dirn):
	for fname in os.listdir(dirn):
		if not ".PYC" in fname.upper():
			module_temp = imp.load_source('module', dirn+"/"+fname)
			for funcname in dir(module_temp):
				if funcname.upper().startswith("INIT"):
					if eval("module_temp."+funcname+"(root)")==False:
						print "Loading of '"+funcname+"' from '"+fname+"' in '"+dirn+"' failed: False"
