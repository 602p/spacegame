from __future__ import division
import state, ship, pygame, random, tasks, overlay_gui, interdiction_gui, sys, math, parralax, sectors
from logging import debug, info, warning, error, critical

class RunningGameState(state.State):
	def first_start(self):

		
		# for i in xrange(0,10):
		# 	self.entities.append(ship.create_ship(self.root, "cargo_transport_test", random.randint(-300,300), random.randint(-300,300)))
		self.generated=[]

		random.seed(0)
		for i in range(random.randint(30,60)):
			self.generated.append([[random.randint(-8000,8000), random.randint(-6000,6000)], random.sample(self.root.gamedb.get_startswith("bg_nebula"), 1)[0]])
		# for i in range(random.randint(5,10)):
		# 	self.generated.append([[random.randint(-8000,8000), random.randint(-6000,6000)], random.sample(self.root.gamedb.get_startswith("bg_planet"), 1)[0]])

		

		self.parralax_scroller=parralax.ParralaxStarfieldScroller(
			self.root.renderspace_size,
			[
				parralax.StarfieldLayer(20, (255,255,255), 2, -1.25),
				parralax.StarfieldLayer(30, (225,225,225), 2, -1.5),
				parralax.StarfieldLayer(40, (200,200,200), 3, -1),
				parralax.StarfieldLayer(40, (150,150,150), 2, -0.6)
			]
		)

		# self.entities=[]
		# self.entities=[
		# 	ship.create_ship(self.root, "cargo_transport_test", 100, 100, ai=False),
		# 	# ship.create_ship(self.root, "ss_bajor_ds9", -100, -100),
		# 	# ship.create_ship(self.root, "ss_f9_jumpgate", -2000, -2000)
		# ]


		#self.entities[0].targeted=self.entities[1]

		# self.player=self.entities[0]
	def start(self):
		info("=================================STARTING GAME STATE==========================")
	def update_and_render(self):
		#self.root.screen.screen.fill((0,0,0))
		self.root.screen.screen.blit(self.root.gamedb("large_black_bg"), (0,0))
		if self.root.settings["graphics"]["render_stars"]:
			self.parralax_scroller.render(self.root.screen.screen)

		self.root.particlemanager.update()
		for n in self.generated:
			self.root.screen.blit(n[1], n[0])

		if pygame.key.get_pressed()[self.root.settings["keybindings"]["turn_left"]]:
			self.player.rigidbody.rotate(self.player.turn_rate)
		if pygame.key.get_pressed()[self.root.settings["keybindings"]["turn_right"]]:
			self.player.rigidbody.rotate(-self.player.turn_rate)
		if pygame.key.get_pressed()[self.root.settings["keybindings"]["accelerate"]]:
			self.player.exert_engine()
		if pygame.key.get_pressed()[self.root.settings["keybindings"]["decelerate"]]:
			self.player.exert_reverse_engine()
		if pygame.key.get_pressed()[self.root.settings["keybindings"]["fire_item"]]:
			self.player.fire_item_in_hardpoint(self.player.selected_wep)

		update_time=1/self.root.fps

		self.root.screen.draw_rect((0,255,0), pygame.Rect(-sectors.SECTORSIZE,-sectors.SECTORSIZE,sectors.SECTORSIZE*2,sectors.SECTORSIZE*2), 10)

		tasks.run_group(self.root, "render_before_particles")
		self.root.particlemanager.draw(self.root.screen)
		
		locked_by=0
		self.root.quest_manager.update()
		
		tasks.run_group(self.root, "render_before_entities")
		for entitiy in reversed(self.entities): #run thru in reverse so player is always on top
			if not entitiy.kill:
				entitiy.tick(self.root.screen, update_time)
				if entitiy.targeted==self.player and isinstance(entitiy, ship.Ship):
					locked_by+=1
				# if self.g_render_lines:
				# 	self.root.screen.draw_line((255,255,255), (self.player.rigidbody.x, self.player.rigidbody.y), (entitiy.rigidbody.x, entitiy.rigidbody.y), 2)
		tasks.run_group(self.root, "render_after_entities")
		if locked_by>0:
			self.root.screen.screen.blit(self.root.gamedb("font_standard_small").render("LOCKED BY "+str(locked_by)+" SHIPS!", 0, (255,0,0)), (150,0))


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
				self.root.screen.screen.fill((0,0,0))
				self.parralax_scroller.render(self.root.screen.screen)
				self.root.particlemanager.update()
				self.root.particlemanager.draw(self.root.screen)
				pygame.display.flip()
				i+=1
			if not interdiction_gui.interdict_yn(self.root, "GAME OVER", "You have died. Were playing "+self.player.name+" ("+self.player.id_string+"). Killed by TODO. Better luck next time :(", "RESET", "QUIT"):
				sys.exit()
				pygame.quit()
			else:
				self.root.state_manager.states["game"].first_start()

		self.entities=[]

		self.entities=new_entities

		#print self.player.rigidbody._vector.angle-math.degrees(math.atan2(self.player.rigidbody.y-self.player.targeted.rigidbody.y, self.player.targeted.rigidbody.x-self.player.rigidbody.x))

		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("T: "+str(self.root.game_time), False, (0,255,255)), (0,580-200))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("F: "+str(self.root.clock.get_fps()), False, (0,255,255)), (0,600-200))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("A: "+str(self.player.rigidbody.get_angle()), False, (0,255,255)), (0,620-200))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("V: "+str(self.player.rigidbody.get_magnitude()), False, (0,255,255)), (0,640-200))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("X: "+str(self.player.rigidbody.x), False, (0,255,255)), (0,680-200))
		self.root.screen.screen.blit(self.root.gamedb.get_asset("font_standard_small").render("Y: "+str(self.player.rigidbody.y), False, (0,255,255)), (0,660-200))	

		self.player.damage.render_systems_full(self.root.screen.screen, self.root.gamedb.get_asset("font_standard_small"))
		self.player.damage.render_infobox(self.root.screen.screen, self.root.gamedb.get_asset("font_standard_very_small"), 1150, 50, 0)
		overlay_gui.render_wepbar(self.root, self, self.player, 402, 632)

		if self.player.targeted:
			if self.root.settings["debug"]["raycast"]:self.root.screen.draw_line((255,0,0), (self.player.rigidbody.x, self.player.rigidbody.y), (self.player.targeted.rigidbody.x, self.player.targeted.rigidbody.y), 2)
			overlay_gui.render_rangefinder(self.root, self.player, [self.player.targeted.rotated_rect.centerx, self.player.targeted.rotated_rect.centery])
			self.player.targeted.damage.render_infobox(self.root.screen.screen, self.root.gamedb.get_asset("font_standard_very_small"), 1150, 430, 1)


		self.root.igconsole.render((0,625))
		#overlay_gui.render_rangefinder(self.root, self.player, [self.entities[1].rotated_rect.centerx, self.entities[1].rotated_rect.centery])


		self.root.screen.set_offset((self.player.rigidbody.x-(self.root.renderspace_size[0]/2), self.player.rigidbody.y-(self.root.renderspace_size[1]/2)))
		self.parralax_scroller.move_to(self.player.rigidbody.x, self.player.rigidbody.y)

		tasks.run_group(self.root, "render_last")

		self.root.game_time+=min(1/max(self.root.fps,0.001),0.1)
		if self.root.settings["debug"]["raycast"]:
			for entitiy in reversed(self.entities): #run thru in reverse so player is always on top
				if not entitiy.kill:
					self.root.screen.draw_line((255,255,255), (self.player.rigidbody.x, self.player.rigidbody.y), (entitiy.rigidbody.x, entitiy.rigidbody.y), 2)
	def suspend(self):
		self.root.background_gamerun_screen=self.root.screen.screen.copy()
		#darkenx=pygame.Surface(self.root.background_gamerun_screen.get_size())
        #darkenx.fill((0,0,0))
        #darkenx.set_alpha(128)
        #self.root.background_gamerun_screen.blit(darkenx,(0,0))

	def process_events(self, events):
		for e in events:
			if e.type==pygame.KEYDOWN:
				if e.key == self.root.settings["keybindings"]["prev_item"]:
					self.player.selected_wep-=1
					if self.player.selected_wep==-1:
						self.player.selected_wep=len(self.player.hardpoints)-1
				elif e.key == self.root.settings["keybindings"]["next_item"]:
					self.player.selected_wep+=1
					if self.player.selected_wep==len(self.player.hardpoints):
						self.player.selected_wep=0
				elif e.key == pygame.K_HOME:
					self.entities.append(ship.create_ship(self.root, "destroyer_transport_test", 1000, 1000))
					self.entities[-1].targeted=self.player
					self.entities[-1].rigidbody.x=0
					self.entities[-1].rigidbody.y=0
					self.player.targeted=self.entities[-1]
				elif e.key == pygame.K_BACKQUOTE: pass #hiding window
				elif e.key == pygame.K_ESCAPE:
					self.root.state_manager.start_interdicting("generic_ui", self.root.gamedb("sgcui_settings"))
			elif e.type==pygame.VIDEORESIZE:
				print e
				print "gsresize"
				print
				debug("GameState resize")
				self.parralax_scroller.bindall(self.root.renderspace_size)
			elif e.type==pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
				for entitiy in self.entities:
					if entitiy.can_be_targeted:
						if self.root.screen.get_t_rect(entitiy.rotated_rect).collidepoint(pygame.mouse.get_pos()):
							self.player.targeted=entitiy
			for ext in self.root.extentions:
				self.root.extentions[ext].event_state("game", e)

	def _get_entity_by_id(self, hid):
		"""NOTE: DO NOT USE. USE entitybase.get_entitiy_by_id INSTEAD!"""
		for entity in self.entities:
			try:
				if entity.hash_id==hid:
					return entity
			except AttributeError:
				pass
		return None

class CreditsState(state.InterdictingState):
	def internal_update(self):
		self.root.screen.screen.blit(self.root.gamedb("credits_screen"), (0,0))
		
	def process_events(self, events):
		for e in events:
			if e.type==pygame.MOUSEBUTTONDOWN or e.type==pygame.KEYDOWN:
				self.finish()
