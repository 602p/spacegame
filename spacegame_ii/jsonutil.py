from logging import debug, info, warning, error, critical
import lang
ju_debug=True
import logging
module_logger=logging.getLogger("sg.jsonutil")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical
debug("ju_debug: "+str(ju_debug))

def get_expanded_json(gamedb, json):
	o=expand_object(gamedb, json)
	if ju_debug and o!=json:
		debug("=================================JSON INITIAL============================")
		debug(str(json))
		debug("=================================JSON   FINAL============================")
		debug(str(o))
		debug("=========================================================================")
	return o

def get_expanded_json2(json):
	import absroot
	return get_expanded_json(absroot.gamedb, json)

def expand_object(db, j):
	if type(j)==dict:
		return expand_dict(db, j)
	if type(j)==list:
		return expand_list(db, j)
	if type(j)==str or type(j)==unicode:
		return expand_string(db, j)
	return j

def expand_dict(db, j):
	#Expand all %+s, not ovveriding, then
	new={}
	for k in filter(lambda x:x.startswith("%+"), j.keys()):
		if k.startswith("%+") and k.endswith("%"):
			#debug("DICT_EXAND_MODE: Expanding "+k)
			assetname=k.replace("%", '').replace("+", '')
			db.get_meta(assetname)["trefs"]+=1
			new.update(db.get_asset(assetname))
	#Expand all normal
	for k in j.keys():
		new[k]=expand_object(db, j[k])
	#Expand all %++s with ovveride
	for k in filter(lambda x:x.startswith("%++"), j.keys()):
		if k.startswith("%+") and k.endswith("%"):
			#debug("DICT_EXAND_MODE: Expanding woveride "+k)
			db.get_meta("cfg_"+k.replace("%", '').replace("+", ''))["trefs"]+=1
			new.update(db.get_asset("cfg_"+k.replace("%", '').replace("+", '')))
	return new

def expand_list(db, j):
	new=[]
	for i in j:
		if ( type(i)==str or type(i)==unicode ) and ( i.startswith("%+") and i.endswith("%") ):
			new.extend(expand_string(db, i))
		else:
			new.append(expand_object(db, i))
	return new

def expand_string(db, j):
	if j.startswith("%") and j.endswith("%"):
		if ju_debug: debug("Replacing node "+j+" with node '"+str(db.get_asset("cfg_"+j.replace("%", '').replace("+", '')))+"'")
		db.get_meta("cfg_"+j.replace("%", '').replace("+", ''))["trefs"]+=1
		return db.get_asset("cfg_"+j.replace("%", '').replace("+", ''))
	return lang.gettext(j)

def dget(dictx, att, default, root=None):
	if att in dictx:
		if att.startswith("%"):
			return root.gamedb.get_asset("cfg_"+att.strip("%"))
		return dictx[att]
	return default

def get_inserts(o):
	l=[]
	if type(o)==dict:
		for k, v in o.iteritems():
			l.extend(get_inserts(k))
			l.extend(get_inserts(v))
	if type(o)==list:
		for v in o:
			l.extend(get_inserts(v))
	if type(o)==str or type(o)==unicode:
		if o.startswith("%") and o.endswith("%"):
			l.append(o.replace("%","").replace("+",""))
	return l