from __future__ import division
from logging import debug, info, warning, error, critical
import logging, sys, traceback, datetime, ai
logging.basicConfig(filemode='w', filename='spacegame.log',level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
debug("Logging Started")
import ship, item, primitives, pygame, rotutil, particles, random, tasks, state, gamestate, extention_loader
import assets, pyconsole, interdiction_gui, overlay_gui

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

screen=pygame.display.set_mode(renderspace_size)
pygame.display.set_caption("Spacegame Alpha")

scrollingscreen=rotutil.ScrollingWorldManager(screen)

class R:pass
root=R()

ship.init(root)
item.init(root)
primitives.init(root)
tasks.init(root)
ai.init(root)
tasks.add_group(root, "render_last")
root.particlemanager=particles.ParticleManager()
root.screen=scrollingscreen
root.state_manager=state.StateManager(root)
root.console = pyconsole.Console(screen,(0,0,1300,200),localsx=locals())
root.gamedb=assets.GameAssetDatabase()


root.igconsole = overlay_gui.IngameRenderedConsole(root, 10)
root.igconsole.enable_debug()

root.settings={
	"render_particles":True,
	"render_stars":True
}

debug("Loaded all SG extentions")

root.renderspace_size=renderspace_size

extention_loader.load_all_packages(root, 'extentions')

debug("Loaded all packages")

root.state_manager.add_state(gamestate.RunningGameState(), "game")
root.state_manager.add_state(gamestate.RunningGamePausedState(), "game_paused")
root.state_manager.goto_state("game")
root.game_time=0
g=root.state_manager.states["game"]

debug("StateManager initilized")

root.clock=pygame.time.Clock()

pygame.event.set_blocked([pygame.KEYUP, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
	pygame.VIDEORESIZE, pygame.VIDEOEXPOSE, pygame.ACTIVEEVENT])

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

	for e in pygame.event.get():
		if e.type==pygame.QUIT:
			run=0
		elif e.type==pygame.KEYDOWN:
			if e.key == pygame.K_BACKQUOTE and pygame.key.get_mods() & pygame.KMOD_CTRL:
				root.console.set_active()
			elif e.key == pygame.K_ESCAPE:
				root.state_manager.goto_state("game_paused")
			else:
				pygame.event.post(e)
		else:
			pygame.event.post(e)
	root.clock.tick()
	pygame.event.pump()

	if root.clock.get_fps()<1:
		root.fps=999
	else:
		root.fps=root.clock.get_fps()

	if pygame.event.peek(pygame.QUIT):run=0
	root.console.process_input()
	try:
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
			pygame.draw.line(fps_surf, (0,255,255), (fps_xo-1, 400-fps_osps*100), (fps_xo, 400-fps_sps*100))
			fps_osps=fps_sps
		# if fps_xo>1300:
		# 	fps_surf.fill((0,0,0))
		# 	pygame.draw.line(fps_surf, (255,0,0), (0, 60), (1300,60))
		# 	pygame.draw.line(fps_surf, (0,0,255), (0, 40), (1300,40))
		# 	pygame.draw.line(fps_surf, (0,255,0), (0, 0), (1300,0))
		# pygame.draw.line(fps_surf, (0,255,255), (fps_xo-1, 400-fps_ofps), (fps_xo, 400-root.fps))
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("FPS: "+str(root.fps), False, (0,255,255)), (0,310))
		root.screen.screen.blit(root.gamedb.get_asset("font_standard_very_small").render("S/S: "+str(fps_sps)+"/1", False, (0,255,255)), (0,320))
		#root.screen.screen.blit(fps_surf, (0,200))
		# fps_xo+=1
		# fps_ofps=root.fps

	root.console.draw()
	root.igconsole.render((0,550))
	pygame.display.flip()
	if eventclear_tick==10:
		pygame.event.clear()
		eventclear_tick=0
	eventclear_tick+=1