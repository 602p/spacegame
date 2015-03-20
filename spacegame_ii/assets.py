import os, pygame, json, extention_loader, sys, traceback
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json
import logging
module_logger=logging.getLogger("sg.assets")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


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
		self.metadata={"$BLANK":{"refs":0, "trefs":0}}
		def _process_ldir(basepath, metadata, path):
			n_2 = path.replace("{$LDIR$}", metadata.get("udpath", "(udpath not availible???)"))
			print n_2
			if not "{$LDIR$}" in path:
				print "Prepending..."
				n_2=os.path.join(basepath, n_2)
			return n_2
		def load_image(node, basepath, metadata={}):
			node["path"]=_process_ldir(basepath, metadata, node["path"])
			debug("Loading image "+node["path"])
			i=pygame.image.load(os.path.join(node["path"]))
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
		self.register_loader("image",load_image)

		def load_cursor(node, basepath, metadata={}):
			debug("Loading cursor "+node["path"])
			i=pygame.image.load(os.path.join(basepath+node["path"].replace("{$LDIR$}", metadata.get("udpath", "(udpath not availible???)"))))
			return [i.convert_alpha(), node.get("hotspot", (0,0))]
		self.register_loader("gfxcursor",load_cursor)

		def load_sound(node, basepath, metadata={}):
			node["path"]=_process_ldir(basepath, metadata, node["path"])
			debug("Loading sound "+node["path"])
			i=pygame.mixer.Sound(node["path"])
			if "volume" in node:
				i.set_volume(node["volume"])
			return i
		self.register_loader("sound",load_sound)

		def load_font(node, basepath, metadata={}):
			debug("Loading font "+node["path"].replace("{$LDIR$}", metadata.get("udpath", "(udpath not availible???)")))
			s=20
			if "size" in node:
				s=node["size"]
			f=pygame.font.Font(basepath+node["path"], s)
			f.set_bold(node.get("default_bold", False))
			return f
		self.register_loader("font",load_font)

		def load_sysfont(node, basepath, metadata={}):
			s=20
			if "size" in node:
				s=node["size"]
			debug("Loading sysfont "+str(node["sys_name"])+" of size "+str(node["size"]))
			f = pygame.sysfont.SysFont(node["sys_name"], s)
			f.set_bold(node.get("default_bold", False))
			return f
		self.register_loader("sysfont",load_sysfont)

		def load_json(node, basepath, metadata={}):
			debug("Loading JSON '"+str(node["json"])[:10]+"...'")
			return node["json"]
		self.register_loader("json",load_json)

	def register_loader(self, key, func):
		self.loaders[key]=func
		debug("Registered loader '"+key+"'::"+str(func))

	def load_with_loader(self, node, basepath, path, console=None):
		# print node["type"]
		# print node["type"] in self.loaders.keys()
		# print
		try:
			debug("Applying loader:'"+node["type"]+"' infer from:'"+node["name"]+"'...")
			self.metadata[node["name"]]={"basepath":basepath, "apath":path, "udpath":os.path.dirname(path), "node":node, "refs":0, "trefs":0}
			self.assets[str(node["name"])]=self.loaders[str(node["type"])](get_expanded_json(self, node), basepath, self.metadata[node["name"]])
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
					if console: extention_loader.post_and_flip(console, "--> Delaying load of "+path+" until after "+i, italic=1, color=(255,255,0))
		if do_load:
			for i in data:
				debug("Load ["+"::"+path+"]:"+str(data.index(i)))
				self.load_with_loader(i, basepath, path, console)
				self.loaded_nodes.append(i["name"])
		else:
			self.delayed_load_nodes.append(fullnode)
			self.delayed_load_nodes[-1]["__basepath"]=basepath
			self.delayed_load_nodes[-1]["__path"]=path

	def process_delayed_load(self, console):
		if console: extention_loader.post_and_flip(console, "(Processing delayed_load nodes...)", bold=1, color=(255,255,0))
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
		d = self.assets[key]
		if key in self.metadata:
			self.metadata[key]["refs"]+=1
		if isinstance(d, basestring):
			if d.startswith("$ASSETREDIR:"):
				return self.get_asset(d.replace("$ASSETREDIR:","",1))
		return self.assets[key]

	def get_meta(self, key):
		return self.metadata[key]

	def get_startswith(self, key):
		r=[]
		for i in self.assets.keys():
			if i.startswith(key):
				r.append(self.assets[i])
		return r

	def __call__(self, key):
		return self.get_asset(key)
