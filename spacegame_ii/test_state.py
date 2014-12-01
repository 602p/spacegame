from __future__ import division
from logging import debug, info, warning, error, critical
import logging
logging.basicConfig(filemode='w', filename='spacegame.log',level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
debug("Logging Started")
import ship, item, primitives, pygame, rotutil, particles, random, tasks, state, gamestate, extention_loader, assets, pyconsole, interdiction_gui

def credits():
	print("Spacegame was made by:")
	print("Creator/Main Coder: Louis Goessling")
	print("Idea Generator/Artist/Some Code: Sebastian Waterhouse")
	print("Pyconsole from: John Schank")
	print("Art assets by MillionthVector (http://millionthvector.blogspot.de)")
	print("Misc. assets from Opengameart.org")

pygame.init()

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
tasks.add_group(root, "render_last")
root.particlemanager=particles.ParticleManager()
root.screen=scrollingscreen
root.state_manager=state.StateManager(root)
root.console = pyconsole.Console(screen,(0,0,1300,200),localsx=locals())
root.gamedb=assets.GameAssetDatabase()

root.renderspace_size=renderspace_size

extention_loader.load_all_packages(root, 'extentions')

root.state_manager.add_state(gamestate.RunningGameState(), "game")
root.state_manager.add_state(gamestate.RunningGamePausedState(), "game_paused")
root.state_manager.goto_state("game")
root.game_time=0
g=root.state_manager.states["game"]

root.clock=pygame.time.Clock()

pygame.event.set_blocked([pygame.KEYUP, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
	pygame.VIDEORESIZE, pygame.VIDEOEXPOSE, pygame.ACTIVEEVENT])

run=True

eventclear_tick=0

i=0
while i!=20:
	pygame.display.update()
	i+=1

while run:

	for e in pygame.event.get():
		if e.type==pygame.QUIT:
			run=0
		elif e.type==pygame.KEYDOWN:
			if e.key == pygame.K_BACKQUOTE and pygame.key.get_mods() & pygame.KMOD_CTRL:
				root.console.set_active()
			elif e.key == pygame.K_ESCAPE:
				root.state_manager.goto_state("game_paused")
			elif e.key == pygame.K_3:
				print interdiction_gui.interdict_yn(root, "TEST_TITLE", "text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text ")
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
	root.state_manager.run_tick()
	root.console.draw()
	pygame.display.flip()
	if eventclear_tick==10:
		pygame.event.clear()
		eventclear_tick=0
	eventclear_tick+=1
