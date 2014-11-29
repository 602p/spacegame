from __future__ import division
import state, ship, pygame, random, tasks

class RunningGameState(state.State):
	def first_start(self):
		self.player=ship.create_ship(self.root, "cargo_transport_test", 100, 100)
		self.ship2=ship.create_ship(self.root, "destroyer_transport_test", 100, 100)
		self.player.targeted=self.ship2
		self.ship2.rigidbody.x=0
		self.ship2.rigidbody.y=0
		self.stars=pygame.transform.scale(pygame.image.load("stars-1.png").convert_alpha(), (500,500))
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

		self.generated=[]

		random.seed(0)
		for i in range(random.randint(30,60)):
			self.generated.append([[random.randint(-8000,8000), random.randint(-6000,6000)],nebulae[random.randint(0,len(nebulae)-1)]])
		for i in range(random.randint(5,10)):
			self.generated.append([[random.randint(-8000,8000), random.randint(-6000,6000)],planets[random.randint(0,len(planets)-1)]])
		self.ship2.rigidbody.x=0
		self.ship2.rigidbody.y=0
	def start(self):
		pass
	def update_and_render(self):
		self.root.screen.screen.fill((0,0,0))
		self.root.particlemanager.update()
		for y in range(-6000,6000,self.stars.get_height()):
			for x in range(-8000,8000,self.stars.get_width()):
				self.root.screen.blit(self.stars, (x,y))
		for n in self.generated:
			self.root.screen.blit(n[1], n[0])

		if pygame.key.get_pressed()[pygame.K_LEFT]:
			self.player.rigidbody.rotate(self.player.turn_rate)
		if pygame.key.get_pressed()[pygame.K_RIGHT]:
			self.player.rigidbody.rotate(-self.player.turn_rate)
		if pygame.key.get_pressed()[pygame.K_UP]:
			self.player.exert_engine()
		if pygame.key.get_pressed()[pygame.K_DOWN]:
			self.player.exert_reverse_engine()
		if pygame.key.get_pressed()[pygame.K_SPACE]:
			self.player.fire_item_in_hardpoint(0)
		self.ship2.exert_engine()

		for e in pygame.event.get():
			if e.type==pygame.KEYDOWN:
				if e.key == pygame.K_1:
					self.player.damage(1)
				else:
					pygame.event.post(e)
			else:
					pygame.event.post(e)

		self.root.particlemanager.draw(self.root.screen)
		self.ship2.rigidbody.rotate(20)
		update_time=1/max(self.root.clock.get_fps(), 0.001)
		self.ship2.tick(self.root.screen, update_time)
		self.player.tick(self.root.screen, update_time)
		
		self.root.screen.screen.blit(self.root.font.render("F: "+str(self.root.clock.get_fps()), False, (0,255,255)), (0,600))
		self.root.screen.screen.blit(self.root.font.render("A: "+str(self.player.rigidbody.get_angle()), False, (0,255,255)), (0,620))
		self.root.screen.screen.blit(self.root.font.render("V: "+str(self.player.rigidbody.get_magnitude()), False, (0,255,255)), (0,640))
		self.root.screen.screen.blit(self.root.font.render("X: "+str(self.player.rigidbody.x), False, (0,255,255)), (0,680))
		self.root.screen.screen.blit(self.root.font.render("Y: "+str(self.player.rigidbody.y), False, (0,255,255)), (0,660))	

		self.player.damage.render_full(self.root.screen.screen, self.root.font)
		self.player.damage.render_infobox(self.root.screen.screen, self.root.font_small, 1150, 50)

		self.root.screen.set_offset((self.player.rigidbody.x-(self.root.renderspace_size[0]/2), self.player.rigidbody.y-(self.root.renderspace_size[1]/2)))

		tasks.run_group(self.root, "render_last")
	def suspend(self):
		self.root.background_gamerun_screen=self.root.screen.screen.copy()
		#darkenx=pygame.Surface(self.root.background_gamerun_screen.get_size())
        #darkenx.fill((0,0,0))
        #darkenx.set_alpha(128)
        #self.root.background_gamerun_screen.blit(darkenx,(0,0))

class RunningGamePausedState(state.State):
	def first_start(self):
		self.petr=self.root.font_large.render("PRESS ENTER TO RESUME", 1, (255,255,255))
		self.paused=self.root.font_large.render("PAUSED", 1, (255,255,255))
	def update_and_render(self):
		self.root.screen.screen.fill((0,0,0))
		if 'background_gamerun_screen' in dir(self.root):
			self.root.screen.screen.blit(self.root.background_gamerun_screen, (0,0))
		self.root.screen.screen.blit(self.paused, ((self.root.renderspace_size[0]/2)-(self.paused.get_width()/2), 50))
		self.root.screen.screen.blit(self.petr, ((self.root.renderspace_size[0]/2)-(self.petr.get_width()/2), 250))
		for e in pygame.event.get():
			if e.type==pygame.KEYDOWN:
				print "a"
				if e.key==pygame.K_RETURN:
					print "b"
					self.state_manager.goto_state("game")
