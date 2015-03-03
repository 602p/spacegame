import os, item, ship, serialize, primitives, imp, json, fnmatch, pygame, time, sys, dialog, quests, faction, state, absroot, textwrap
from logging import debug, info, warning, error, critical
import logging
module_logger=logging.getLogger("sg.extention_loader")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def load_all_packages(root, dirn, console=None):
	info("Loading Plugins")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Loading Plugins   V V V", bold=1, color=(0,255,0))
	load_plugins(root, dirn, console)
	info("Doing last plugin init...")
	for ext in root.extentions:
		root.extentions[ext].after_plugins_load()
	info("Loading Assetkeys")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Loading Assets    V V V", bold=1, color=(0,255,0))
	load_assetkeys(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_assets_load()
	info("Loading items")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Compiling Items   V V V", bold=1, color=(0,255,0))
	load_items(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_items_load()
	info("Loading Ships")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V   Compiling Ships   V V V", bold=1, color=(0,255,0))
	load_ships(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_ships_load()

	info("Loading dialog")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V  Installing Dialog  V V V", bold=1, color=(0,255,0))
	load_dialog(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_dialog_load()

	info("Loading factions")
	#if console: post_and_flip(console, "| | |                     | | |", bold=1, color=(0,255,0))
	if console: post_and_flip(console, "V V V Installing Factions V V V", bold=1, color=(0,255,0))
	load_factions(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_faction_load()

	info("Loading quests")
	if console: post_and_flip(console, "V V V  Compiling  Quests  V V V", bold=1, color=(0,255,0))
	load_quests(root, dirn, console)
	for ext in root.extentions:
		root.extentions[ext].after_quests_load()

	if console:
		post_and_flip(console, "LOADING FINISHED!", bold=1, italic=1, color=(0,255,0))
		post_and_flip(console, "Loaded "+str(len(root.gamedb.assets))+" assets")
		post_and_flip(console, "Loaded "+str(len(root.item_factories))+" items")
		post_and_flip(console, "Loaded "+str(len(root.ship_factories))+" ships")
		post_and_flip(console, "Loaded "+str(root.dialog_manager.count_pools())+" speech pools ("+str(root.dialog_manager.count_speeches())+" speechIs distributed)")
		post_and_flip(console, "Loaded "+str(len(root.quest_factories))+" quests")
		post_and_flip(console, "(Sectors get loaded at runtime C: )")
		time.sleep(2.5)

def safepost(console, text, bold=0, italic=0, underline=0, color=(255,255,255), bg=(0,0,0), debugmsg=False):
	if console:
		post_and_flip(console, text, bold=bold, italic=italic, underline=underline, color=color, bg=bg, debugmsg=debugmsg)

def findall(dirn, pattern):
	matches=[]
	for root, dirnames, filenames in os.walk(dirn):
		for filename in fnmatch.filter(filenames, pattern):
			matches.append(os.path.join(root, filename))
	return sorted(matches)

def load_assetkeys(root, dirn, console):
	for rootn, dirnames, filenames in os.walk(dirn):
		if "plugin.id" in filenames:
			with open(rootn+"/plugin.id", 'r') as fd:
				debug("Loading a plugin.id from "+rootn)
				data=json.load(fd)
				create_master_ext(data["name"], desc="&"+data.get("desc", "Package notifier for $name")+" [from "+rootn+"]", color=data.get("color", (127,127,255)), bold=data.get("bold", 1), italic=data.get("italic", 0))
		for filename in fnmatch.filter(filenames, "*.assetkey"):
			root.gamedb.load_assetfile(os.path.join(rootn, filename), rootn.split("\\")[0]+"\\"+rootn.split("\\")[1]+"\\", console)
	root.gamedb.process_delayed_load(console)

def load_plugins(root, dirn, console):
	for rn in findall(dirn, "*.plugin.py"):
		if console: post_and_flip(console, "Loading Plugin '"+rn+"'...", color=(255,255,255))
		load_plugin(root, rn, console)

def load_quests(root, dirn, console):
	for rn in findall(dirn, "*.quest"):
		if console: post_and_flip(console, "Loading Quest '"+rn+"'...", color=(255,255,255))
		quests.load_file(root, rn)

def load_items(root, dirn, console):
	for rn in findall(dirn, "*.item"):
		if console: post_and_flip(console, "Loading Item '"+rn+"'...", color=(255,255,255))
		item.load_file(root, rn)

def load_factions(root, dirn, console):
	for rn in findall(dirn, "*.faction"):
		if console: post_and_flip(console, "Loading Faction '"+rn+"'...", color=(255,255,255))
		faction.load_file(root, rn)

def load_dialog(root, dirn, console):
	for rn in findall(dirn, "*.talk"):
		if console: post_and_flip(console, "Loading dialog '"+rn+"'...", color=(255,255,255))
		dialog.load_file(root, rn)

def load_ships(root, dirn, console):
	for rn in sorted(findall(dirn, "*.ship")):
		if console: post_and_flip(console, "Loading Ship '"+rn+"'...", color=(255,255,255))
		ship.load_file(root, rn)	

def load_galaxy(root, dirn, console):
	import sectors #dumb hack to fix circular imports
	c=0
	for rn in findall(dirn, "*.sector"):
		c+=1
		if console: post_and_flip(console, "Loading Sector '"+rn+"'...", color=(255,255,255))
		sectors.load_file(root, rn)		
	return c

def load_plugin(root, fname, console):
	if not ".PYC" in fname.upper():
		debug("Load plugin '"+fname+"'")
		key=fname.replace("\\", "").replace(".", "")
		exec key+" = imp.load_source('"+key+"', fname)"
		debug("Key mapped as '"+key+"' 	")
		for funcname in eval("dir("+key+")"):
			if funcname.upper().startswith("INIT"):
				debug("Run init '"+fname+"'::"+funcname)
				if console: post_and_flip(console, "Initilizing Plugin '"+fname+"::"+funcname+"'...", color=(255,255,255))
				if eval(key+"."+funcname+"(root, console)")==False:
					warning( "Loading of '"+funcname+"' from '"+fname+"' in '"+dirn+"' failed: False")

def post_and_flip(console, *args, **kwargs):
	console.post(*args, **kwargs)
	console.render((0,0))
	for i in pygame.event.get():
		if i.type==pygame.QUIT:
			sys.exit(1)
	pygame.display.flip()
	#time.sleep(0.005)

class HookableExtention(object):
	name="[unset-name]"
	def __init__(self, root):
		self.root=root
		
	def event_root(self, event):
		pass

	def event_state(self, state, event):
		pass

	def last_load(self):
		pass

	def after_plugins_load(self):
		pass

	def after_assets_load(self):
		pass

	def after_items_load(self):
		pass

	def after_ships_load(self):
		pass

	def after_dialog_load(self):
		pass

	def after_quests_load(self):
		pass

	def after_faction_load(self):
		pass

	def tick(self, state):
		pass

	def get_text(self):
		return self.name+" -- "+self.get_desc()

	def get_desc(self):
		return "Installed"
		
	def get_color(self):
		return (255,255,255)

	def get_bold(self):
		return 0

	def get_italic(self):
		return 0

class ExtentionInfoClass(state.InterdictingState):
	def first_start(self):
		self.basepos=0
	def internal_update(self):
		absroot.screen.screen.fill((0,0,0))
		pos=self.basepos
		for name, ext in absroot.extentions.iteritems():
			absroot.gamedb("LOADER_font_plugin_list").set_bold(ext.get_bold())
			absroot.gamedb("LOADER_font_plugin_list").set_italic(ext.get_italic())
			absroot.screen.screen.blit(absroot.gamedb("LOADER_font_plugin_list").render(name+": "+ext.get_text(), 1, ext.get_color()), [0, pos])
			pos+=absroot.gamedb("LOADER_font_plugin_list").size("A")[1]
		absroot.gamedb("LOADER_font_plugin_list").set_bold(0)
		absroot.gamedb("LOADER_font_plugin_list").set_italic(0)

	def process_events(self, events):
		for e in events:
			if e.type==pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					self.finish()
			if e.type==pygame.MOUSEBUTTONDOWN:
				if e.button==5:
					self.basepos+=20
				if e.button==4:
					self.basepos-=20

class AssetInfoClass(state.InterdictingState):
	def first_start(self):
		self.basepos=0

	def internal_update(self):
		absroot.screen.screen.fill((0,0,0))
		root=absroot
		self.pos=self.basepos
		self.render_lines("")
		self.render_lines("Press D to dump asset info.")
		self.render_lines(str(len(root.gamedb.assets))+" assets: "+(", ".join([x+"["+str(root.gamedb.metadata[x]["refs"])+","+str(root.gamedb.metadata[x]["trefs"])+"]" for x in sorted(root.gamedb.assets.keys(), key=lambda k: -root.gamedb.metadata[k]["refs"]-root.gamedb.metadata[k]["trefs"])])), (255,255,255))
		self.render_lines(str(len(root.item_factories))+" items: "+(", ".join(sorted(root.item_factories))), (255,125,125))
		self.render_lines(str(len(root.ship_factories))+" ships: "+(", ".join(sorted(root.ship_factories.keys()))), (125,125,255))
		self.render_lines(str(root.dialog_manager.count_pools())+" speech pools: "+(", ".join(sorted(root.dialog_manager.pools.keys()))), (125,255,125))
		self.render_lines(str(len(root.quest_factories))+" quests: "+(", ".join(sorted(root.quest_factories.keys()))),  (255,125,255))

	def render_lines(self, text, color=(255,255,255)):
		text=textwrap.wrap(text, int(absroot.renderspace_size[0]/absroot.gamedb("LOADER_font_small").size("_")[0])-2)
		for l in text:
			absroot.screen.screen.blit(absroot.gamedb("LOADER_font_small").render(l, 1, color), (0, self.pos))
			self.pos+=absroot.gamedb("LOADER_font_small").size("|")[1]
		self.pos+=absroot.gamedb("LOADER_font_small").size("|")[1]

	@staticmethod
	def dump_start():
		with open("assetlist.txt", 'w') as fd:pass

	@staticmethod
	def dump_lines(text, _=0):
		with open("assetlist.txt", 'a') as fd:
			fd.write(text+"\n")

	@staticmethod
	def dump_assetlist():
		root=absroot
		debug("Dumping assetlist...")
		AssetInfoClass.dump_start()
		debug("Writing...")
		AssetInfoClass.dump_lines(str(len(root.gamedb.assets))+" assets: "+(", ".join([x+"["+str(root.gamedb.metadata[x]["refs"])+","+str(root.gamedb.metadata[x]["trefs"])+"]" for x in sorted(root.gamedb.assets.keys(), key=lambda k: -root.gamedb.metadata[k]["refs"]-root.gamedb.metadata[k]["trefs"])])), (255,255,255))
		AssetInfoClass.dump_lines(str(len(root.item_factories))+" items: "+(", ".join(sorted(root.item_factories))), (255,125,125))
		AssetInfoClass.dump_lines(str(len(root.ship_factories))+" ships: "+(", ".join(sorted(root.ship_factories.keys()))), (125,125,255))
		AssetInfoClass.dump_lines(str(root.dialog_manager.count_pools())+" speech pools: "+(", ".join(sorted(root.dialog_manager.pools.keys()))), (125,255,125))
		AssetInfoClass.dump_lines(str(len(root.quest_factories))+" quests: "+(", ".join(sorted(root.quest_factories.keys()))),  (255,125,255))
		AssetInfoClass.dump_lines("="*30)
		for i in root.gamedb.assets.keys():
			AssetInfoClass.dump_lines("<ASSET> "+i+" ("+str(type(root.gamedb.assets[i]))+"): "+str(root.gamedb.assets[i]))
			if i in root.gamedb.metadata:
				AssetInfoClass.dump_lines(" <META> "+i+": "+str(root.gamedb.metadata[i]))
			else:
				AssetInfoClass.dump_lines(" <NOMETA>")
		AssetInfoClass.dump_lines("="*30)
		for i in root.item_factories.keys():
			AssetInfoClass.dump_lines("<ITEM> "+i+": "+str(root.item_factories[i]))
		AssetInfoClass.dump_lines("="*30)
		for i in root.ship_factories.keys():
			AssetInfoClass.dump_lines("<SHIP> "+i+": "+str(root.ship_factories[i]))
		AssetInfoClass.dump_lines("="*30)
		for i in root.dialog_manager.pools.keys():
			AssetInfoClass.dump_lines("<POOL> "+i+": "+str(root.dialog_manager.pools[i]))
		AssetInfoClass.dump_lines("="*30)
		for i in root.quest_factories.keys():
			AssetInfoClass.dump_lines("<QUEST> "+i+": "+str(root.quest_factories[i]))
		debug("Done")

	def process_events(self, events):
		for e in events:
			if e.type==pygame.MOUSEBUTTONDOWN or e.type==pygame.KEYDOWN:
				if e.type==pygame.KEYDOWN:
					if e.key==pygame.K_d:
						self.dump_assetlist()

						return
					if e.key==pygame.K_ESCAPE:
						self.finish()
				if e.type==pygame.MOUSEBUTTONDOWN:
					if e.button==5:
						self.basepos+=20
					if e.button==4:
						self.basepos-=20
					
def create_master_ext(name_, desc='Package notifier for $name', color=(127,127,255), bold=1, italic=0):
	debug("Adding a _Master plugin id, name:"+name_)
	desc=desc.replace("$name", name_)
	class _Master(HookableExtention):
		name=name_
		def get_desc(self):
			return desc

		def get_bold(self):
			return bold

		def get_italic(self):
			return italic

		def get_color(self):
			return color
	absroot.extentions["m_"+name_]=_Master(absroot)