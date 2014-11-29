from __future__ import division
import ship, item, primitives, pygame, rotutil, particles, random, tasks, state, gamestate, extention_loader
import pyconsole

pygame.init()

renderspace_size=(1300,700)

screen=pygame.display.set_mode(renderspace_size)

scrollingscreen=rotutil.ScrollingWorldManager(screen)

class R:pass
root=R()

ship.init(root)
item.init(root)
primitives.init(root)
tasks.init(root)
tasks.add_group(root, "render_last")
root.particlemanager=particles.ParticleManager()
root.font=pygame.font.Font("kenvector_future_thin.ttf", 15)
root.font_large=pygame.font.Font("kenvector_future_thin.ttf", 25)
root.font_small=pygame.font.Font("kenvector_future_thin.ttf", 10)
root.console_font=pygame.font.SysFont("", 15)
root.screen=scrollingscreen
root.state_manager=state.StateManager(root)
root.console = pyconsole.Console(screen,(0,0,1300,200),localsx=locals())

root.renderspace_size=renderspace_size

def test(r, n, p):
	def _internal(t, r):
		p=t.data[1]
		n=t.data[0]
		r.screen.draw_line(n["color"], p.get_center(), p.parent.targeted.rotated_rect.center, n["thickness"])
	tasks.add_task(r, "render_last", tasks.Task(_internal, n["duration"], (n, p)))
	return True
primitives.register_primitive(root, "render_laser_beam", test)

def test2(r, n, p):
	p.parent.targeted.damage(n["damage"])
	return True
primitives.register_primitive(root, "simple_damage", test2)

extention_loader.load_all_packages(root, 'extentions')

root.state_manager.add_state(gamestate.RunningGameState(), "game")
root.state_manager.add_state(gamestate.RunningGamePausedState(), "game_paused")
root.state_manager.goto_state("game")
g=root.state_manager.states["game"]

root.clock=pygame.time.Clock()

pygame.event.set_blocked([pygame.KEYUP, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
	pygame.VIDEORESIZE, pygame.VIDEOEXPOSE, pygame.ACTIVEEVENT])

run=True

eventclear_tick=0

while run:
	root.clock.tick()
	pygame.event.pump()
	
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
	if pygame.event.peek(pygame.QUIT):run=0
	root.console.process_input()
	root.state_manager.run_tick()
	root.console.draw()
	pygame.display.flip()
	if eventclear_tick==10:
		pygame.event.clear()
		eventclear_tick=0
	eventclear_tick+=1