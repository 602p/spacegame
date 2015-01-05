from __future__ import division
from logging import debug, info, warning, error, critical
import logging, sys, traceback, datetime, ai
logging.basicConfig(filemode='w', filename='spacegame.log',level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
debug("Logging Started")
import ship, item, primitives, pygame, rotutil, particles, random, tasks, state, gamestate, extention_loader
import assets, pyconsole, interdiction_gui, overlay_gui, ui_states
import sgc

allowdebug=True

def credits():
	print("Spacegame was made by:")
	print("Creator/Main Coder: Louis Goessling")
	print("Idea Generator/Artist/Some Code: Sebastian Waterhouse")
	print("Pyconsole from: John Schank")
	print("Art assets by MillionthVector (http://millionthvector.blogspot.de)")
	print("Misc. assets from Opengameart.org")

if allowdebug:
	def g_spawnship(name, a=True, w=True):
		g.entities.append(ship.create_ship(root, name, g.player.rigidbody.x, g.player.rigidbody.y, w, a))

pygame.init()
debug("Pygame started")

renderspace_size=(1300,700)

screen=sgc.surface.Screen(renderspace_size, pygame.DOUBLEBUF)
pygame.display.set_caption("Spacegame Alpha")



class R:pass
root=R()

root.settings={
	"particles_level":5,
	"render_stars":True,
	"keybindings":{
		"interact":101 #K_e
	},
	"debug":{
		"raycast":False,
		"overrender":False
	}
}


scrollingscreen=rotutil.ScrollingWorldManager(root, screen.image)

ship.init(root)
item.init(root)
primitives.init(root)
tasks.init(root)
ai.init(root)
tasks.add_group(root, "render_last")
root.particlemanager=particles.ParticleManager()
root.screen=scrollingscreen
root.state_manager=state.StateManager(root)
root.console = pyconsole.Console(screen.image,(0,0,1300,200),localsx=locals())
root.gamedb=assets.GameAssetDatabase()


root.igconsole = overlay_gui.IngameRenderedConsole(root, 5)
root.igconsole.enable_debug()


root.game_time=0

debug("Loaded all SG extentions")

root.renderspace_size=renderspace_size

extention_loader.load_all_packages(root, 'extentions')

debug("Loaded all packages")

root.state_manager.add_state(gamestate.RunningGameState(), "game")
root.state_manager.add_state(gamestate.RunningGamePausedState(), "game_paused")
root.state_manager.add_state(ui_states.GenericUIInterdictor(), "generic_ui")
root.state_manager.goto_state("game")

g=root.state_manager.states["game"]

debug("StateManager initilized")

root.clock=pygame.time.Clock()

pygame.event.set_blocked([pygame.KEYUP, pygame.VIDEOEXPOSE, pygame.ACTIVEEVENT])

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

eventclear_tick=0

pygame.mouse.set_cursor(*pygame.cursors.broken_x)

while run:
	events=pygame.event.get()
	for e in events:
		
		if e.type==pygame.QUIT:
			debug("Shutting Down")
			sys.exit()
		elif e.type==pygame.KEYDOWN:
			if e.key == pygame.K_BACKQUOTE and pygame.key.get_mods() & pygame.KMOD_CTRL:
				root.console.set_active()
			elif e.key == pygame.K_ESCAPE:
				root.state_manager.goto_state("game_paused")
		elif e.type==pygame.VIDEORESIZE:
			debug("Root resize")
			root.renderspace_size=e.dict['size']
			root.screen=rotutil.ScrollingWorldManager(sgc.surface.Screen(root.renderspace_size, pygame.RESIZABLE))
			#root.screen.rect=((0,0), root.renderspace_size)
	root.clock.tick()
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
		if not interdiction_gui.interdict_yn(root, "ERROR", "Error in state_manager.run_tick. WARNING: IF YOU CONTINUE GAME MAY CORRUPT OR CONTINUE TO ERROR. Error in log; please submit! Crash datum:"+" "*100+str(e), "RESUME", "QUIT"):
			sys.exit()

	if fps_log_enable:
		if datetime.datetime.now()-fps_last>datetime.timedelta(seconds=1):
			fps_last=datetime.datetime.now()
			fps_sps=root.game_time-fps_last_gt
			fps_last_gt=root.game_time
			fps_osps=fps_sps
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("FPS: "+str(root.fps), False, (0,255,255)), (0,310))
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("S/S: "+str(fps_sps)+"/1", False, (0,255,255)), (0,320))
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("LEN(EVENTS): "+str(len(events)), False, (0,255,255)), (0,330))

	root.console.draw()
	#pygame.draw.line(root.screen.screen, (255,0,0), (0,0), root.renderspace_size, 20)
	
	pygame.display.flip()

	