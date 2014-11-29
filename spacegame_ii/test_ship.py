from __future__ import division
import ship, item, primitives, pygame, rotutil, particles, random, tasks

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
root.screen=scrollingscreen

def test(r, n, p):
	def _internal(t, r):
		p=t.data[1]
		n=t.data[0]
		r.screen.draw_line(n["color"], p.get_center(), ship2.rotated_rect.center, n["thickness"])
	tasks.add_task(r, "render_last", tasks.Task(_internal, n["duration"], (n, p)))
	return True
primitives.register_primitive(root, "render_laser_beam", test)

item.load_dir(root, "extentions/stock/items")
ship.load_dir(root, "extentions/stock/ships")

player=ship.create_ship(root, "cargo_transport_test", 100, 100)
ship2=ship.create_ship(root, "destroyer_transport_test", 200, 200)
ship2.velocity=3.5
stars=pygame.transform.scale(pygame.image.load("stars-1.png").convert_alpha(), (500,500))
nebulae=[
	pygame.image.load("extentions/stock/image/bg-elements/nebula-1.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/bg-elements/nebula-2.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/bg-elements/nebula-3.png").convert_alpha()
]
planets=[
	pygame.image.load("extentions/stock/image/planets/planet-1.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-2.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-3.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-4.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-5.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-6.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-7.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-8.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-9.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-10.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-11.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-12.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-13.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-14.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-15.png").convert_alpha(),
	pygame.image.load("extentions/stock/image/planets/planet-16.png").convert_alpha(),
]

generated=[]

random.seed(0)

for i in range(random.randint(30,60)):
	generated.append([[random.randint(-8000,8000), random.randint(-6000,6000)],nebulae[random.randint(0,len(nebulae)-1)]])
for i in range(random.randint(5,10)):
	generated.append([[random.randint(-8000,8000), random.randint(-6000,6000)],planets[random.randint(0,len(planets)-1)]])

clock=pygame.time.Clock()

run=True

while run:
	clock.tick(60)
	screen.fill((0,0,0))
	root.particlemanager.update()
	for y in range(-6000,6000,stars.get_height()):
		for x in range(-8000,8000,stars.get_width()):
			scrollingscreen.blit(stars, (x,y))
	for n in generated:
		scrollingscreen.blit(n[1], n[0])
	
	for event in pygame.event.get():
		if event.type==pygame.QUIT: run=0
	if pygame.key.get_pressed()[pygame.K_LEFT]:
		player.turn(player.turn_rate)
	if pygame.key.get_pressed()[pygame.K_RIGHT]:
		player.turn(-player.turn_rate)
	if pygame.key.get_pressed()[pygame.K_UP]:
		player.exert_engine()
	if pygame.key.get_pressed()[pygame.K_DOWN] and player.velocity>0:
		player.exert_reverse_engine()
	root.particlemanager.draw(scrollingscreen)
	ship2.angle+=0.1
	ship2.render(scrollingscreen)
	ship2.update_pos()
	player.render(scrollingscreen)
	player.update_pos()

	screen.blit(root.font.render("A: "+str(player.angle), False, (0,255,255)), (0,620))
	screen.blit(root.font.render("V: "+str(player.velocity), False, (0,255,255)), (0,640))
	screen.blit(root.font.render("X: "+str(player.x), False, (0,255,255)), (0,680))
	screen.blit(root.font.render("Y: "+str(player.y), False, (0,255,255)), (0,660))
	
	

	scrollingscreen.set_offset((player.x-(renderspace_size[0]/2), player.y-(renderspace_size[1]/2)))

	if pygame.key.get_pressed()[pygame.K_SPACE]:
		player.fire_item_in_hardpoint(0)

	# screen.blit(globalspace, (0,0), (player.x-(renderspace_size[0]/2), player.y-(renderspace_size[1]/2),
	#  renderspace_size[0]/2, renderspace_size[1]/2))
	
	tasks.run_group(root, "render_last")

	pygame.display.flip()
