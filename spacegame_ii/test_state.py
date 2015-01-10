from __future__ import division
from logging import debug, info, warning, error, critical
import logging, sys, traceback, datetime, ai
logging.basicConfig(filemode='w', filename='spacegame.log',level=logging.DEBUG, format='[%(asctime)s] %(levelname)s\t: %(message)s')
debug("Logging Started")
import ship, item, primitives, pygame, rotutil, particles, random, tasks, state, gamestate, extention_loader
import assets, pyconsole, interdiction_gui, overlay_gui, ui_states
import sgc, serialize, gfxcursor

allowdebug=True

def credits():
	print("Spacegame was made by:")
	print("Creator/Main Coder: Louis Goessling")
	print("Idea Generator/Artist/Some Code: Sebastian Waterouse")
	print("Pyconsole from: John Schank")
	print("Art assets by MillionthVector (http://millionthvector.blogspot.de)")
	print("Misc. assets from Opengameart.org")

if allowdebug:
	def g_spawnship(name, a=True, w=True):
		g.entities.append(ship.create_ship(root, name, g.player.rigidbody.x, g.player.rigidbody.y, w, a))

pygame.init()
debug("Pygame started")

class R:pass
root=R()

serialize.load_settings(root)

renderspace_size=root.settings["graphics"]["window_size"]

screen=sgc.surface.Screen(renderspace_size, pygame.DOUBLEBUF, root.settings["graphics"]["color_depth"])
pygame.display.set_caption("Spacegame Alpha")

scrollingscreen=rotutil.ScrollingWorldManager(root, screen.image)
root.screen=scrollingscreen

ship.init(root)
item.init(root)
primitives.init(root)
tasks.init(root)
ai.init(root)
ui_states.init(root)

root.gfxcursor=gfxcursor.GfxCursor(root, root.screen.screen)

root.particlemanager=particles.ParticleManager()

root.state_manager=state.StateManager(root)
root.console = pyconsole.Console(screen.image,(0,0,1300,200),localsx=locals())
root.gamedb=assets.GameAssetDatabase()


root.igconsole = overlay_gui.IngameRenderedConsole(root, 5)
root.igconsole.enable_debug()


root.game_time=0

debug("Loaded all SG extentions")

root.renderspace_size=renderspace_size

info("Loading loader packages")
extention_loader.load_all_packages(root, 'loader')
info("Loading core packages")
root.loader_renderer=overlay_gui.IngameRenderedConsole(root, root.renderspace_size[1]/root.gamedb("LOADER_font_mono").size("A")[1], 200, "LOADER_font_mono")
extention_loader.load_all_packages(root, 'extentions', root.loader_renderer if root.settings["graphics"]["loader_screen"] else None)

debug("Loaded all packages")

root.state_manager.add_state(gamestate.RunningGameState(), "game")
root.state_manager.add_state(gamestate.RunningGamePausedState(), "game_paused")
root.state_manager.factories["generic_ui"]=state.InterdictingStateFactory(ui_states.GenericUIInterdictor)
root.state_manager.goto_state("game")

g=root.state_manager.states["game"]

debug("StateManager initilized")

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

info("Doing last plugin init...")
for ext in root.extentions:
	root.extentions[ext].last_load()

if root.settings["graphics"]["gfxcursor"]:root.gfxcursor.setCursorFromAsset("cursor_triangle_glow")

while run:
	events=pygame.event.get()

	for ext in root.extentions:
		for e in events:
			root.extentions[ext].event_root(events)

	for e in events:
		
		if e.type==pygame.QUIT:
			debug("Shutting Down")
			sys.exit()
		elif e.type==pygame.KEYDOWN:
			if e.key == pygame.K_BACKQUOTE and pygame.key.get_mods() & pygame.KMOD_CTRL:
				root.console.set_active()
			elif e.key == pygame.K_ESCAPE:
				root.state_manager.start_interdicting("generic_ui", root.gamedb("sgcui_settings"))
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
	else:
		root.fps=root.clock.get_fps()

	if pygame.event.peek(pygame.QUIT):run=0
	root.console.process_input(events)
	try:
		root.state_manager.process_events(events)
		root.state_manager.run_tick()
	except BaseException as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		error("================ROOT ERROR=====================")
		for i in traceback.format_exception(exc_type, exc_value, exc_traceback): error(i)
		ui_states.interdict_yn(root, "StateMGR Error", "ERROR in state_manager.run_tick. Game my corrupt if continued...%n"+str(e), "Continue", "Quit", callback_n=lambda s:pygame.quit())

	if fps_log_enable:
		if datetime.datetime.now()-fps_last>datetime.timedelta(seconds=1):
			fps_last=datetime.datetime.now()
			fps_sps=root.game_time-fps_last_gt
			fps_last_gt=root.game_time
			fps_osps=fps_sps
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("FPS: "+str(root.clock.get_fps()), False, (0,255,255)), (0,310))
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("S/S: "+str(fps_sps)+"/1", False, (0,255,255)), (0,320))
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("LEN(EVENTS): "+str(len(events)), False, (0,255,255)), (0,330))

	root.console.draw()
	#pygame.draw.line(root.screen.screen, (255,0,0), (0,0), root.renderspace_size, 20)

	root.gfxcursor.show()
	
	flip_screen()

	