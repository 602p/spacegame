import os, pygame, json
from logging import debug, info, warning, error, critical

class GameAssetDatabase:
	def __init__(self):
		self.assets={"$BLANK":pygame.Surface((0,0))}
		self.loaders={}
		def load_image(node, basepath):
			i=pygame.image.load(basepath+node["path"])
			if "convert_alpha" in node:
				if not node["convert_alpha"]:
					return i
			return i.convert_alpha()
		self.loaders["image"]=load_image

		def load_sound(node, basepath):
			i=pygame.mixer.Sound(basepath+node["path"])
			if "volume" in node:
				i.set_volume(node["volume"])
			return i
		self.loaders["sound"]=load_sound

		def load_font(node, basepath):
			s=20
			if "size" in node:
				s=node["size"]
			return pygame.font.Font(basepath+node["path"], s)
		self.loaders["font"]=load_font

		def load_sysfont(node, basepath):
			s=20
			if "size" in node:
				s=node["size"]
			return pygame.sysfont.SysFont(node["sys_name"], s)
		self.loaders["sysfont"]=load_sysfont

		def load_json(node, basepath):
			return node["json"]
		self.loaders["json"]=load_json

	def register_loader(self, func, key):
		self.loaders["key"]=func

	def load_with_loader(self, node, basepath):
		assert node["type"] in self.loaders, "Loader type '"+node["type"]+"' not defined [GameAssetDatabase]"
		self.assets[node["name"]]=self.loaders[node["type"]](node, basepath)

	def load_assetfile(self, path, basepath):
		for i in json.load(open(path))["assets"]:
			self.load_with_loader(i, basepath)
			debug("Load node ["+path+"::"+basepath+"]: "+str(i))

	def get_asset(self, key):
		return self.assets[key]
