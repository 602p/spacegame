from __future__ import division
import state, ship, pygame, random, tasks, overlay_gui, interdiction_gui, sys
from logging import debug, info, warning, error, critical

class RunningGameState(state.State):
	def first_start(self):
		self.entities=[ship.create_ship(self.root, "cargo_transport_test", 100, 100)]
		self.player=self.entities[0]
		self.entities.append(ship.create_ship(self.root, "destroyer_transport_test", 100, 100))
		self.player.targeted=self.entities[1]
		self.entities[1].targeted=self.player
		self.entities[1].rigidbody.x=0
		self.entities[1].rigidbody.y=0
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
		self.entities[1].rigidbody.x=0
		self.entities[1].rigidbody.y=0

		self.player.selected_wep=0
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
			self.player.fire_item_in_hardpoint(self.player.selected_wep)
		try:
			self.entities[1].exert_engine()
			self.entities[1].rigidbody.rotate(self.entities[1].turn_rate)
		except BaseException: pass

		for e in pygame.event.get():
			if e.type==pygame.KEYDOWN:
				if e.key == pygame.K_1:
					self.player.damage(1)
				if e.key == pygame.K_2:
					self.entities[1].fire_item_in_hardpoint(0)
					self.entities[1].fire_item_in_hardpoint(1)
				if e.key == pygame.K_4:
					raise IndexError("Test error")
				if e.key == pygame.K_a:
					self.player.selected_wep-=1
					if self.player.selected_wep==-1:
						self.player.selected_wep=len(self.player.hardpoints)-1
				if e.key == pygame.K_s:
					self.player.selected_wep+=1
					if self.player.selected_wep==len(self.player.hardpoints):
						self.player.selected_wep=0
				else:
					pygame.event.post(e)
			else:
					pygame.event.post(e)

		self.root.particlemanager.draw(self.root.screen)
		
		update_time=1/self.root.fps
		for entitiy in reversed(self.entities): #run thru in reverse so player is always on top
			if not entitiy.kill:
				entitiy.tick(self.root.screen, update_time)
		
		new_entities=[]
		for e in self.entities:
			if not e.kill: new_entities.append(e)
			else:
				try:
					for e2 in self.entities:
						if e2.targeted==e:
							e2.targeted=None
				except BaseException as e:
					error("ERROR REMOVING TARGETED")
					error(e)

		if self.player.kill:
			i=0
			while i!=200:
				self.root.particlemanager.update()
				self.root.particlemanager.draw(self.root.screen)
				i+=1
			interdiction_gui.interdict_ok(self.root, "GAME OVER", "You have died. Were playing "+self.player.name+" ("+self.player.id_string+"). Killed by TODO. Better luck next time :(", "QUIT")
			pygame.quit()
			sys.exit()

		self.entities=[]

		self.entities=new_entities


		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("T: "+str(self.root.game_time), False, (0,255,255)), (0,580))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("F: "+str(self.root.clock.get_fps()), False, (0,255,255)), (0,600))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("A: "+str(self.player.rigidbody.get_angle()), False, (0,255,255)), (0,620))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("V: "+str(self.player.rigidbody.get_magnitude()), False, (0,255,255)), (0,640))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("X: "+str(self.player.rigidbody.x), False, (0,255,255)), (0,680))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("Y: "+str(self.player.rigidbody.y), False, (0,255,255)), (0,660))	

		self.player.damage.render_systems_full(self.root.screen.screen, self.root.gamedb.get_asset("font_standard_small"))
		self.player.damage.render_infobox(self.root.screen.screen, self.root.gamedb.get_asset("font_standard_very_small"), 1150, 50, 0)
		overlay_gui.render_wepbar(self.root, self, self.player, 186, 632)
		
		if self.player.targeted:
			self.player.targeted.damage.render_infobox(self.root.screen.screen, self.root.gamedb.get_asset("font_standard_very_small"), 1150, 530, 1)

		self.root.screen.set_offset((self.player.rigidbody.x-(self.root.renderspace_size[0]/2), self.player.rigidbody.y-(self.root.renderspace_size[1]/2)))

		tasks.run_group(self.root, "render_last")

		self.root.game_time+=min(1/max(self.root.fps,0.001),0.1)
	def suspend(self):
		self.root.background_gamerun_screen=self.root.screen.screen.copy()
		#darkenx=pygame.Surface(self.root.background_gamerun_screen.get_size())
        #darkenx.fill((0,0,0))
        #darkenx.set_alpha(128)
        #self.root.background_gamerun_screen.blit(darkenx,(0,0))

class RunningGamePausedState(state.State):
	def first_start(self):
		self.petr=self.root.gamedb.get_asset("font_standard_large").render("PRESS ENTER TO RESUME", 1, (255,255,255))
		self.paused=self.root.gamedb.get_asset("font_standard_large").render("PAUSED", 1, (255,255,255))
	def update_and_render(self):
		self.root.screen.screen.fill((0,0,0))
		if 'background_gamerun_screen' in dir(self.root):
			self.root.screen.screen.blit(self.root.background_gamerun_screen, (0,0))
		self.root.screen.screen.blit(self.paused, ((self.root.renderspace_size[0]/2)-(self.paused.get_width()/2), 50))
		self.root.screen.screen.blit(self.petr, ((self.root.renderspace_size[0]/2)-(self.petr.get_width()/2), 250))
		for e in pygame.event.get():
			if e.type==pygame.KEYDOWN:
				if e.key==pygame.K_RETURN:
					self.state_manager.goto_state("game")
