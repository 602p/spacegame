import os, pygame, json, sys, traceback, absroot, jsonutil, tasks
from logging import debug, info, warning, error, critical
from jsonutil import get_expanded_json, get_expanded_json2
import logging
extention_loader=None
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

def load_where_endswith(extention):
    if extention not in absroot.gamedb.json_extentions:
        absroot.gamedb.json_extentions.append(extention)
    def load_where_endswith_w(func):
        debug("Using load_where_endswith bind "+str(func)+" to files that end in '"+extention+"'")
        if extention not in absroot.gamedb.extention_loaders:
            absroot.gamedb.extention_loaders[extention]=[]
        absroot.gamedb.extention_loaders[extention].append(func)
        return func
    return load_where_endswith_w

def _process_ldir(basepath, metadata, path):
            #print path
            n_2 = path.replace("{$LDIR$}", metadata.get("udpath", "(udpath not availible???)"))
            #print n_2
            if not "{$LDIR$}" in path:
                #print "Prepending..."
                n_2=os.path.join(basepath, n_2)
            return n_2

class GameAssetDatabase(object):
    json_extentions=[
        '.assetkey',
        '.item',
        '.ship',
        '.faction',
        '.quest',
        '.talk',
        '.sector'
    ]

    loading_systems=[]
    def __init__(self):
        self.assets={"$BLANK":pygame.Surface((0,0))}
        self.loaders={}
        self.delayed_load_files=[]
        self.metadata={"$BLANK":{"refs":0, "trefs":0}}

        
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

        self.extention_loaders={
            ".assetkey":[self.load_assetkey]
        }

    def postload_init(self):
        global extention_loader
        import extention_loader

    def register_loader(self, key, func):
        self.loaders[key]=func
        debug("Registered loader '"+key+"'::"+str(func))

    def load_with_loader(self, node, basepath, path, console=None):
        # print node["type"]
        # print node["type"] in self.loaders.keys()
        # print
        try:
            debug("Applying loader:'"+node["type"]+"' infer from:'"+node["name"]+"'...")
            #print "Loading "+node["name"]
            self.metadata[node["name"]]={"basepath":basepath, "apath":path, "udpath":path, "node":node, "refs":0, "trefs":0}
            self.assets[str(node["name"])]=self.loaders[str(node["type"])](get_expanded_json(self, node), basepath, self.metadata[node["name"]])
        except KeyError as e:
            error("Loader "+node["type"]+" not found! (probably)")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error("================ERROR LOG=====================")
            for i in traceback.format_exception(exc_type, exc_value, exc_traceback): error(i)
            if console: extention_loader.post_and_flip(console, "ASSETKEY ERROR! KeyError: '"+traceback.format_exception(exc_type, exc_value, exc_traceback)[-1]+"'", color=(255,0,0), bold=1)
            tasks.display_hanging_message("An unknown error appeared while loading the asset `"+node.get("name", "[no name, this is probably the problem]")+"` [KeyError]: Check log ("+str(e)+")", color=(255,0,0))
        except BaseException as e:
            tasks.display_hanging_message("An unknown error appeared while loading the asset `"+node.get("name", "[no name, this is probably the problem]")+"`: Check log ("+str(e)+")", color=(255,0,0))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error("================ERROR LOG=====================")
            for i in traceback.format_exception(exc_type, exc_value, exc_traceback): error(i)
            if console: extention_loader.post_and_flip(console, "ASSETKEY ERROR! KeyError: '"+traceback.format_exception(exc_type, exc_value, exc_traceback)[-1]+"'", color=(255,0,0), bold=1)

    def load_assetkey(self, json_data, basepath, dirn, filen, console):
        #print path
        for asset in json_data["assets"]:
            self.load_with_loader(asset, basepath, dirn, console)

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
        if key not in self.assets and "cfg_"+key in self.assets:
            warning("A request for `"+key+"` was made (key does not exist) and `cfg_` was prepended.")
            key="cfg_"+key
            
        elif key not in self.assets and key.replace("cfg_","") in self.assets:
            warning("A request for `"+key+"` was made (key does not exist) and `cfg_` was removed.")
            key=key.replace("cfg_","")
            
        #print "Request for "+key
        d = self.assets[key]
        if key in self.metadata:
            self.metadata[key]["refs"]+=1
        if isinstance(d, basestring):
            if d.startswith("$ASSETREDIR:"):
                return self.get_asset(d.replace("$ASSETREDIR:","",1))
        return self.assets[key]

    def get_meta(self, key):
        # print self.metadata.keys()
        # print key
        if key not in self.metadata and "cfg_"+key in self.metadata:
            warning("A request for `"+key+"` was made (key does not exist) and `cfg_` was prepended.")
            key="cfg_"+key
            
        elif key not in self.metadata and key.replace("cfg_","") in self.metadata:
            warning("A request for `"+key+"` was made (key does not exist) and `cfg_` was removed.")
            key=key.replace("cfg_","")
            
        # print key
        # print
        return self.metadata[key]

    def has_asset(self, key):
        if key not in self.assets and "cfg_"+key in self.assets:
            warning("A request for `"+key+"` was made (key does not exist) and `cfg_` was prepended.")
            key="cfg_"+key
            
        elif key not in self.assets and key.replace("cfg_","") in self.assets:
            warning("A request for `"+key+"` was made (key does not exist) and `cfg_` was removed.")
            key=key.replace("cfg_","")
            
        return key in self.assets

    def get_startswith(self, key):
        r=[]
        for i in self.assets.keys():
            if i.startswith(key):
                r.append(self.assets[i])
        return r

    def get_where(self, keydict):
        r=[]
        for name, item in self.assets.iteritems():
            f=0
            for k, v in keydict.iteritems():
                if item.get(k)!=v:
                    f=1
            if f:
                r.append(item)
        return r

    def __call__(self, key):
        return self.get_asset(key)

    def load_dir(self, dirn, files, console, pattern):
        #print dirn
        #print os.path.pathsep
        #print dirn.split(os.path.sep)
        if len(dirn.split(os.path.sep))<2:return
        #apath=os.path.dirname(dirn)
        

        basepath=dirn.split(os.path.sep)[0]+os.path.sep+dirn.split(os.path.sep)[1]+os.path.sep
        for filen in files:
            #print files
            if filen.endswith(pattern):
                
                self.load_file(basepath, dirn, filen, console, pattern)
                
                
    def load_file(self, basepath, dirn, filen, console, pattern):
        #print sorted(self.assets.keys())
        #print filen
        with open(dirn+"/"+filen, 'r') as fp:
            json_data=json.load(fp)

        if not "require" in json_data:
            json_data["require"]=[]

        #json_data["require"].extend(jsonutil.get_inserts(json_data)) # <-- Causes assetkeys that define A and then reference it in B to never load
        #print json_data["require"]

        for dep in json_data["require"]:
            if not self.has_asset(dep):
                # print dep
                debug("Dependency '"+dep+"' not met, aborting for now...")
                for config in self.delayed_load_files:
                    if config[0]==basepath and config[1]==dirn and config[2]==filen:
                        # print "already found"
                        return
                self.delayed_load_files.append((basepath, dirn, filen, console, pattern, dep))
                # print "actually added"
                return

        if pattern in self.extention_loaders:
            debug("Loading "+dirn+"/"+filen+" (matched pattern "+pattern+") using all known loaders")
            t="Loading "+dirn+"/"+filen+" --> "
            for loader in self.extention_loaders[pattern]:
                try:
                    loader(json_data, basepath, dirn, filen, console)
                except BaseException as e:
                    tasks.display_hanging_message("An unknown error appeared while loading the file `"+dirn+"/"+filen+"` : Check log ("+str(e)+")", color=(255,0,0))
                t+=loader.func_name+", "
            t=t[:-2]
            extention_loader.safepost(console, t)


        for config in self.delayed_load_files:
            if config[0]==basepath and config[1]==dirn and config[2]==filen:
                del self.delayed_load_files[self.delayed_load_files.index(config)]
        
        for delayed in self.delayed_load_files:
            if self.has_asset(delayed[-1]):
                self.load_file(*delayed[:-1])