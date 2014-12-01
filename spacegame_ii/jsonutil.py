from logging import debug, info, warning, error, critical

ju_debug=True

def get_expanded_json(gamedb, json):
	o=expand_object(gamedb, json)
	if ju_debug and o!=json:
		debug("=================================JSON INITIAL============================")
		debug(str(json))
		debug("=================================JSON   FINAL============================")
		debug(str(o))
		debug("=========================================================================")
	return o

def expand_object(db, j):
	if type(j)==dict:
		return expand_dict(db, j)
	if type(j)==list:
		return expand_list(db, j)
	if type(j)==str or type(j)==unicode:
		return expand_string(db, j)
	return j

def expand_dict(db, j):
	new={}
	for k in j:
		new[k]=expand_object(db, j[k])
	return new

def expand_list(db, j):
	new=[]
	for i in j:
		new.append(expand_object(db, i))
	return new

def expand_string(db, j):
	if j.startswith("%") and j.endswith("%"):
		if ju_debug: debug("Replacing node "+j+" with node '"+str(db.get_asset("cfg_"+j.replace("%", '')))+"'")
		return db.get_asset("cfg_"+j.replace("%", ''))
	return j

def dget(dictx, att, default, root=None):
	if att in dictx:
		if att.startswith("%"):
			return root.gamedb.get_asset("cfg_"+att.strip("%"))
		return dictx[att]
	return default