import os, pygame, json, extention_loader, sys, traceback
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json

class Spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class GameAssetDatabase:
	def __init__(self):
		self.assets={"$BLANK":pygame.Surface((0,0))}
		self.loaders={}
		self.delayed_load_nodes=[]
		self.loaded_nodes=[]
		def load_image(node, basepath):
			debug("Loading image "+node["path"])
			i=pygame.image.load(os.path.join(basepath+node["path"]))
			ca=1
			if "convert_alpha" in node:
				if not node["convert_alpha"]:
					ca=node["convert_alpha"]
			elif "colorkey" in node:
				#print "converet"
				ca=0
				#i.set_alpha(None)
				i=i.convert()
				if node["colorkey"]==-1:
					node["colorkey"]=i.get_at((0,0))
				i.set_colorkey(node["colorkey"])
			if "scale" in node:
				i=pygame.transform.scale(i, node["scale"])
			if ca:
				return i.convert_alpha()
			else:
				return i.convert()
		self.loaders["image"]=load_image

		def load_image(node, basepath):
			debug("Loading cursor "+node["path"])
			i=pygame.image.load(os.path.join(basepath+node["path"]))
			return [i.convert_alpha(), node.get("hotspot", (0,0))]
		self.loaders["gfxcursor"]=load_image

		def load_sound(node, basepath):
			debug("Loading sound "+node["path"])
			i=pygame.mixer.Sound(basepath+node["path"])
			if "volume" in node:
				i.set_volume(node["volume"])
			return i
		self.loaders["sound"]=load_sound

		def load_font(node, basepath):
			debug("Loading font "+node["path"])
			s=20
			if "size" in node:
				s=node["size"]
			return pygame.font.Font(basepath+node["path"], s)
		self.loaders["font"]=load_font

		def load_sysfont(node, basepath):
			s=20
			if "size" in node:
				s=node["size"]
			debug("Loading sysfont "+str(node["size"])+" of size "+str(node["size"]))
			return pygame.sysfont.SysFont(node["sys_name"], s)
		self.loaders["sysfont"]=load_sysfont

		def load_json(node, basepath):
			debug("Loading JSON '"+str(node["json"])[:10]+"...'")
			return node["json"]
		self.loaders["json"]=load_json

	def register_loader(self, func, key):
		self.loaders["key"]=func

	def load_with_loader(self, node, basepath, console=None):
		# print node["type"]
		# print node["type"] in self.loaders.keys()
		# print
		try:
			debug("Loading node using loader:'"+node["type"]+"' to name:'"+node["name"]+"'... [USING INLINE INSERTION]")
			self.assets[str(node["name"])]=self.loaders[str(node["type"])](get_expanded_json(self, node), basepath)
		except KeyError:
			error("Loader "+node["type"]+" not found! (probably)")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			error("================ERROR LOG=====================")
			for i in traceback.format_exception(exc_type, exc_value, exc_traceback): error(i)
			if console: extention_loader.post_and_flip(console, "ASSETKEY ERROR! KeyError: '"+traceback.format_exception(exc_type, exc_value, exc_traceback)[-1]+"'", color=(255,0,0), bold=1)

	def load_assetfile(self, path, basepath, console=None):
		if console: extention_loader.post_and_flip(console, "Loading Assetkey '"+path+"'...", color=(255,255,255))
		debug("Gonna load "+path)
		fullnode=json.load(open(path))
		data=fullnode["assets"]
		do_load=1
		if "require" in fullnode.keys():
			for i in fullnode["require"]:
				if i not in self.loaded_nodes:
					do_load=0
					debug("(delaying load of "+path+" until after "+i+")")
					if console: extention_loader.post_and_flip(console, "(delaying load of "+path+" until after "+i+")", bold=1)
		if do_load:
			for i in data:
				debug("Load node ["+basepath+"::"+path+"]: INDEX "+str(data.index(i)))
				self.load_with_loader(i, basepath, console)
				self.loaded_nodes.append(i["name"])
		else:
			self.delayed_load_nodes.append(fullnode)
			self.delayed_load_nodes[-1]["__basepath"]=basepath
			self.delayed_load_nodes[-1]["__path"]=path

	def process_delayed_load(self, console):
		if console: extention_loader.post_and_flip(console, "Processing delayed_load nodes...", italic=1, color=(255,255,0))
		self._process_delayed_load(console)

	def _process_delayed_load(self, console):
		next=self.delayed_load_nodes
		self.delayed_load_nodes=[]
		for i in next:
			debug("Trying delayed load of "+i["__path"])
			self.load_assetfile(i["__path"], i["__basepath"], console)
		if len(next)!=0:
			self._process_delayed_load(console)
			
	def get_asset(self, key):
		return self.assets[key]

	def get_startswith(self, key):
		r=[]
		for i in self.assets.keys():
			if i.startswith(key):
				r.append(self.assets[i])
		return r

	def __call__(self, key):
		return self.get_asset(key)
