import assets, absroot

def load_lang_file(json_data, basepath, dirn, filen, console):
	if json_data["id"] not in absroot.langs:
		absroot.langs[json_data["id"]]={}
	absroot.langs[json_data["id"]].update(json_data["translations"])

def gettext(text):
	if "//" in text:
		splits=text.split("//", 1)
		if splits[0].startswith("~"):
			if _has_translation(splits[0]):
				return _get_translation(splits[0])
			else:
				return splits[1]
	else:
		if text.startswith("~"):
			return _get_translation(text.replace("~","",1))
		else:
			if _has_translation(text):
				return _get_translation(text)
			return text

def _get_translation(key):
	if _has_translation(key):
		return absroot.langs[absroot.settings["lang"]][key]
	else:
		return absroot.settings["lang"]+" missing translation for "+key

def _has_translation(key):
	return absroot.settings["lang"] in absroot.langs and key in absroot.langs[absroot.settings["lang"]]

def init():
	absroot.langs={"en":{}}
	absroot.gamedb.json_extentions.insert(0, ".lang")
	absroot.gamedb.extention_loaders[".lang"]=[load_lang_file]