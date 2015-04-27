from __future__ import division
import absroot

SKIP_TO_GAME=0
SKIP_START_ID='startdefun_tt'

from logging import debug, info, warning, error, critical
import logging
logging.basicConfig(filemode='w', filename='spacegame.log',level=logging.DEBUG, format='%(relativeCreated)-6d [%(name)-20s] %(levelname)-8s: %(message)s')
import logging
module_logger=logging.getLogger("sg")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

info("Booting Spacegame_ii "+absroot.version)
debug("...(Logging Started)")

# try:
# 	import psyco
# 	debug("...(Found psyco)")
# 	psyco.full()
# 	info("...(psyco configured)")
# except ImportError:
# 	warning( '...(This game may run faster if you install psyco)' )
# 	print "This game may run faster if you install psyco"

import assets, absroot
absroot.gamedb=assets.GameAssetDatabase()

import ship, item, primitives, pygame, rotutil, particles, random, tasks, state, gamestate, extention_loader, triggers
import pyconsole, interdiction_gui, overlay_gui, ui_states, sectors, newgame, dialog, quests, inventory, atexit, lang
import sgc, serialize, gfxcursor, formatting, pyganim, keymapping, sys, traceback, datetime, ai, types, faction, inventory2
import entitybase as eb
import pygame._view
debug("...(Imports done)")

allowdebug=True

def credits():
	print("Spacegame was made by:")
	print("\tCreator/Main Coder: Louis Goessling")
	print("\tIdea Generator/Artist/Some Code: Sebastian Waterouse")
	print("\tPyconsole from: John Schank")
	print("\tArt assets by MillionthVector (http://millionthvector.blogspot.de)")
	print("\tMisc. assets from Opengameart.org")
	print("\tGFXCursor by Frank Raiser, Pete Shinner")

if allowdebug:
	def g_ss(name, a=True, w=True, k=False):
		g.entities.append(ship.create_ship(root, name, g.player.rigidbody.x, g.player.rigidbody.y, w, a))
		g.entities[-1].keep_in_save=k
	def g_sst():
		g_ss("destroyer_transport_test", 0, 1, 1)
	def g_gs(s1,s2):
		root.galaxy.goto_sector(s1,s2)

pygame.init()
pygame.mixer.init()
pygame.key.set_mods(0) #Hack where CTRL would be held down when launched from sublime with CTRL-B
debug("...(Pygame started)")


root=absroot

root.formatter=formatting.Formatter({"root":root})
root.extentions={}

root.gamedb.postload_init()

root.settings=serialize.load_settings()
if root.settings["debug"]["dump_at_die"]:
	atexit.register(extention_loader.AssetInfoClass.dump_assetlist)

renderspace_size=root.settings["graphics"]["window_size"]
flags=pygame.DOUBLEBUF
if root.settings["graphics"]["fullscreen"]: flags=flags|pygame.FULLSCREEN

screen=sgc.surface.Screen(renderspace_size, flags, root.settings["graphics"]["color_depth"])
pygame.display.set_caption("[Loading...]")

scrollingscreen=rotutil.ScrollingWorldManager(root, screen.image)
root.screen=scrollingscreen

serialize.init(root)
ship.init(root)
item.init(root)
primitives.init(root)
tasks.init(root)
ai.init(root)
ui_states.init(root)
sectors.init(root)
newgame.init(root)
dialog.init(root)
quests.init(root)
eb.init_grufs(root)
faction.init(root)
lang.init()

import music
music.init()

root.gfxcursor=gfxcursor.GfxCursor(root, root.screen.screen)

root.particlemanager=particles.ParticleManager()

root.state_manager=state.StateManager(root)
root.console = pyconsole.Console(screen.image,(0,0,1300,200),localsx=locals())


root.igconsole = overlay_gui.IngameRenderedConsole(root, 5)
root.igconsole.enable_debug()

root.game_time=0
root.fps=999

debug("Loaded all SG extensions")

root.renderspace_size=renderspace_size

info("Loading loader packages")
extention_loader.load_all_packages(root, 'loader')
info("Loading core packages")
root.loader_renderer=overlay_gui.IngameRenderedConsole(root, root.renderspace_size[1]/root.gamedb("LOADER_font_mono").size("A")[1], 200, "LOADER_font_mono")
extention_loader.load_all_packages(root, 'extensions', root.loader_renderer if root.settings["graphics"]["loader_screen"] else None)

debug("Loaded all packages")

root.state_manager.add_state(gamestate.RunningGameState(), "game")

root.state_manager.add_state(newgame.ShipSelectState(), "newgame_selectship")
root.state_manager.factories["ext_info"]=state.InterdictingStateFactory(extention_loader.ExtentionInfoClass)
root.state_manager.factories["ass_info"]=state.InterdictingStateFactory(extention_loader.AssetInfoClass)
root.state_manager.factories["generic_ui"]=state.InterdictingStateFactory(ui_states.GenericUIInterdictor)
root.state_manager.factories["keymapper"]=state.InterdictingStateFactory(keymapping.KeyMapperState)
root.state_manager.factories["credits"]=state.InterdictingStateFactory(gamestate.CreditsState)
root.state_manager.factories["dialog"]=state.InterdictingStateFactory(dialog.DialogState)
root.state_manager.factories["inventory"]=state.InterdictingStateFactory(inventory2.InventoryState2)
root.state_manager.factories["hardpoint_select"]=state.InterdictingStateFactory(inventory2.SlotSelectorState2)

#root.state_manager.goto_state("game")
root.state_manager.start_interdicting("generic_ui", root.gamedb("sgcui_mainmenu"))

g=root.state_manager.states["game"]
#root.player=root.state_manager.states["game"].player
root.gamestate=root.state_manager.states["game"]

debug("StateManager initialized")

root.clock=pygame.time.Clock()

pygame.event.set_blocked([pygame.VIDEOEXPOSE, pygame.ACTIVEEVENT])

fps_log_enable=0
fps_surf=pygame.Surface((1300,300))
fps_ofps=0
fps_osps=0
fps_xo=0
fps_last=datetime.datetime.now()
fps_sps=0
fps_last_gt=0

def tfl():
	global fps_log_enable
	fps_log_enable=not fps_log_enable

run=True;

def flip_screen():
	pygame.display.flip()

eventclear_tick=0

# root.galaxy.gamestate=root.state_manager.states["game"]
# root.galaxy.preprocess_statics()
# root.galaxy.goto_sector(0,0)

ts=None

info("Doing last plugin init...")
for ext in root.extentions:
	root.extentions[ext].last_load()

if root.settings["graphics"]["gfxcursor"]:root.gfxcursor.setCursorFromAsset("cursor_triangle_glow")

if SKIP_TO_GAME:
	serialize.new_game(root, root.gamedb(SKIP_START_ID), 'sel_skipped_name', 'sel_skipped_sname')
else:
	triggers.sg_postevent(triggers.UE_GAME_START)

import fpsgraph
enable_slowmo=False

splash_texts=[]
[splash_texts.extend(x) for x in absroot.gamedb.get_startswith("splashes_")]
splash_text=random.choice(splash_texts)

while run:
	events=pygame.event.get()
	root.last_events_len=len(events)
	fpsgraph.event(events)
	fpsgraph.update(absroot=absroot)
	

	for ext in root.extentions:
		for e in events:
			try:
				root.extentions[ext].event_root(e)
			except BaseException as e:
				tasks.display_hanging_message("An unknown error appeared in the event callback for `"+ext+"`: Check log ("+str(e)+")", color=(255,0,0))
		try:
			root.extentions[ext].tick(root.state_manager.current)
		except BaseException as e:
			tasks.display_hanging_message("An unknown error appeared in the tick for `"+ext+"`: Check log ("+str(e)+")", color=(255,0,0))

	for e in events:
		if e.type==pygame.QUIT:
			debug("Shutting Down")
			info("Writing an autosave to autosave.sgs")
			serialize.save_game(root, "saves/autosave.sgs")
			debug("--Save completed, dying")
			sys.exit()
		elif e.type==pygame.KEYDOWN:
			if e.key == pygame.K_BACKQUOTE and pygame.key.get_mods() & pygame.KMOD_CTRL:
				root.console.set_active()
			if e.key==pygame.K_F1:
				root.quest_manager.start_quest("event_pirate_raid_1")
			if e.key==pygame.K_F2:
				faction.get_faction("klingonempire").try_join(g.player)
			if e.key==pygame.K_F3:
				faction.get_faction("klingonempire").try_leave(g.player)
			if e.key==pygame.K_F4:
				absroot.state_manager.start_interdicting("cutscene_anim", "fsanim_intro_ke")
			if e.key==pygame.K_F7:
				enable_slowmo=not enable_slowmo
			if e.key==pygame.K_F12:
				absroot.state_manager.start_interdicting("ass_info")
		elif e.type==pygame.VIDEORESIZE:
			debug("Root resize")
			root.renderspace_size=e.dict['size']
			root.screen=rotutil.ScrollingWorldManager(sgc.surface.Screen(root.renderspace_size, pygame.RESIZABLE))
		elif e.type==pygame.MOUSEMOTION:
			root.gfxcursor.update(e)
	root.clock.tick(root.settings["graphics"]["target_fps"])
	#pygame.event.pump()

	if root.clock.get_fps()<1:
		root.fps=999
	elif enable_slowmo:
		root.fps=root.settings["debug"]["slowmo_factor"]
	else:
		root.fps=root.clock.get_fps()
	pygame.display.set_caption("Spacegame "+root.version+" ("+str("%3d" % root.fps)+" FPS): "+splash_text)

	if pygame.event.peek(pygame.QUIT):run=0
	root.console.process_input(events)
	try:
		if not root.console.active:
			root.state_manager.process_events(events)
			root.state_manager.run_tick()
	except BaseException as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		error("================ROOT ERROR=====================")
		for i in traceback.format_exception(exc_type, exc_value, exc_traceback): error(i)
		tasks.display_hanging_message("An unknown error appeared in the state manager: Check log ("+str(e)+")", color=(255,0,0))
		# ui_states.interdict_yn(root, "StateMGR Error", "ERROR in state_manager.run_tick. Game my corrupt if continued...%n"+str(e), "Continue", "Quit", callback_n=lambda s:pygame.quit())

	# if fps_log_enable:
	# 	if datetime.datetime.now()-fps_last>datetime.timedelta(seconds=1):
	# 		fps_last=datetime.datetime.now()
	# 		fps_sps=root.game_time-fps_last_gt
	# 		fps_last_gt=root.game_time
	# 		fps_osps=fps_sps
	# 	root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("FPS: "+str(root.clock.get_fps()), False, (0,255,255)), (0,310))
	# 	root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("S/S: "+str(fps_sps)+"/1", False, (0,255,255)), (0,320))
	# 	root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("LEN(EVENTS): "+str(len(events)), False, (0,255,255)), (0,330))


	root.console.draw()
	fpsgraph.render(root.screen.screen)
	#pygame.draw.line(root.screen.screen, (255,0,0), (0,0), root.renderspace_size, 20)

	tasks.run_group(root, 'tooltips')
	tasks.run_group(root, 'messages')

	root.gfxcursor.show()

	root.screen.screen.blit(root.gamedb("LOADER_font_version").render(root.version, 1, (255,0,0)), (0,0))
	
	flip_screen()