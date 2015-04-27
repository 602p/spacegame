import pygame, state, inputbox, ship, ui_states, logging, rotutil, absroot, tooltips, item
from lang import gettext as _t
module_logger=logging.getLogger("sg.inventory2")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

def overlaps(l1, l2):
	for i in l1:
		if i in l2:
			return True
	return False

class SlotSelectorState2(state.InterdictingState):
	def first_start(self):
		debug("Starting SlotSelectorState2")
		self.ship_image=rotutil.aspect_scale(self.params["item"].parent.image, (500,500))
		self.ship_image_pos=(
			(absroot.renderspace_size[0]/2)-(self.ship_image.get_width()/2),
			(absroot.renderspace_size[1]/2)-(self.ship_image.get_height()/2)
		)
		self.scalex=self.ship_image.get_width()/self.params["item"].parent.image.get_width()
		self.scaley=self.ship_image.get_height()/self.params["item"].parent.image.get_height()
		self.scaled_hardpoints=[]
		c=0
		for i in self.params["item"].parent.hardpoints:
			self.scaled_hardpoints.append(
				(pygame.Rect(
					(21+i["x"]*self.scalex)+self.ship_image_pos[0], #Not sure why this works...
					(21+i["y"]*self.scaley)+self.ship_image_pos[1], #Not sure why this works...
					10*self.scalex,
					10*self.scaley
				), c, (255,0,0) if (self.params["item"].parent.get_item_in_hardpoint(c) is not None) else (0,255,0))
			)
			c+=1
		debug("Preloaded...")

	def internal_update(self):
		screen=self.root.screen.screen
		screen.fill((0,0,0))

		screen.blit(self.ship_image, self.ship_image_pos)
		# pygame.draw.line(screen, (255,0,255), (0,0), self.ship_image_pos, 5)
		screen.blit(absroot.gamedb("font_standard_large").render(_t("Select A Slot"), 1, (255,255,255)), (0,0))

		for i in self.scaled_hardpoints:
			pygame.draw.rect(screen, i[2], i[0], 2)
			# pygame.draw.line(screen, (0,0,255), self.ship_image_pos, i[0].topleft, 5)
			if i[2] == (255,0,0):
				self.params["item"].parent.get_item_in_hardpoint(i[1]).tt_delay_update(i[0])

	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
			if event.type==pygame.MOUSEBUTTONDOWN:
				for rect, idx, color in self.scaled_hardpoints:
					if rect.collidepoint(pygame.mouse.get_pos()):
						if color==(0,255,0):
							debug("Equipping idx:" + str(idx))
							self.params["item"].equip(idx)
							self.finish()

	def suspend(self):
		self.root.state_manager.states[self.params["inv_id"]].first_start()

class InventoryState2(state.InterdictingState):
	initial_offset=0
	selected_item=None
	def first_start(self):
		self.INVENTORY_WIDTH=int((absroot.renderspace_size[0]-300)/64)-1
		self.OFFSET=50
		debug("Starting inventoryState2")
		self.ship=self.params["ship"]
		self.is_shop=self.params.get("is_shop",False)
		self.shop_editable=self.params.get("editable", True)
		if self.is_shop:
			self.shop_other=self.params["shop_ship"]
		self.tiles=[] #Array of [ITEM, RECT, IMAGE]
		x=0
		y=0
		for i in sorted(self.ship.inventory, key=lambda i:("000" if i.equipped!=-1 else "")+i.name): #Sort first by equipped
			i.tt_image=None
			image=i.get_inventory_image()
			if i.equipped!=-1:
				pygame.draw.rect(image, (127,127,127), pygame.Rect(2,2,60,60), 2)

			rect=pygame.Rect(x*64, self.OFFSET+self.initial_offset+(y*64), 64, 64)

			self.tiles.append([i, rect, image, True])

			x+=1
			if x>self.INVENTORY_WIDTH:
				x=0
				y+=1

		if self.is_shop:
			y+=2
			x=0
			for i in sorted(self.shop_other.inventory, key=lambda i:("000" if i.equipped!=-1 else "")+i.name):
				i.tt_image=None
				image=i.get_inventory_image()
				pygame.draw.rect(image, (255,255,255), pygame.Rect(2,2,60,60), 2)

				rect=pygame.Rect(x*64, self.OFFSET+self.initial_offset+(y*64), 64, 64)

				self.tiles.append([i, rect, image, False])

				x+=1
				if x>self.INVENTORY_WIDTH:
					x=0
					y+=1
		

	def internal_update(self):
		screen=self.root.screen.screen
		screen.fill((200,200,200))
		screen.blit(absroot.gamedb(self.ship.get_faction_attr("inventory_image", "img_cargobay_default")), (0,0))

		for x in xrange(self.INVENTORY_WIDTH+2):
			pygame.draw.line(screen, (40,40,40), (x*64, 50), (x*64, 690), 2)

		for y in xrange(30):
			pygame.draw.line(screen, (40,40,40), (0, 50+(y*64)), (960, 50+(y*64)), 2)

		for l in self.tiles: 
			screen.blit(l[2], l[1])
			if l[0]==self.selected_item:
				pygame.draw.rect(screen, (0,255,0), pygame.Rect(l[1].left, l[1].top, 64, 64), 2)
			l[0].tt_delay_update(l[1])

		screen.blit(absroot.gamedb(self.ship.get_faction_attr("inventory_image", "img_cargobay_default")).subsurface((0,0,1300,50)), (0,0))
		screen.blit(absroot.gamedb("img_playermenu_inv_sel"), (0,0))
		pygame.draw.rect(screen, (0,0,0), pygame.Rect(962, 50, 400, 700))

		text=_t("INVENTORY MANAGEMENT SYSTEM")
		text+=_t("\nGrey  -->  Equipped")
		text+=_t("\nWhite -->  Not Owned")
		text+=_t("\nGreen -->  Selected")
		text+=_t("\n[=======================================]")
		text+=_t("\nShip   :   ")+str(self.ship.name)
		text+=_t("\nAccel  :   ")+str(int(self.ship.speed/self.ship.get_mass()))
		text+=_t("\nMass   :   ")+str(self.ship.get_mass())+"t"
		text+=_t("\nCargo  :   ")+str(self.ship.get_inventory_mass())+"t"
		text+=_t("\nItems  :   ")+str(sum([x.count for x in self.ship.inventory]))
		if self.is_shop:
			text+=_t("\n[=======================================]\nTRADE MANAGEMENT SYSTEM\nSelect an item and press T to trade")
			text+=_t("\nShop   :   ")+self.shop_other.name
			#text+=_t("\nAccel : "+str(int(self.shop_other.speed/self.shop_other.get_mass())) #Probably don't need this...
			text+=_t("\nMass   :   ")+str(self.shop_other.get_mass())+"t"
			text+=_t("\nCargo  :   ")+str(self.shop_other.get_inventory_mass())+"t"
			text+=_t("\nItems  :   ")+str(sum([x.count for x in self.shop_other.inventory]))

		screen.blit(
			tooltips.render_wrapped_text(text, 300, absroot.gamedb("font_item_desc"), (200,200,200))
			,(962,50)
		)

			
	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
				if self.selected_item:
					if event.key==pygame.K_x:
						if self.selected_item_is_owned:
							self.selected_item.dequip()
							self.first_start()
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Not yours!", button = "OK")
					if event.key==pygame.K_d:
						if self.selected_item_is_owned and self.shop_editable:
							if self.selected_item.equipped==-1:
								self.root.state_manager.states["game"].entities.append(
									ship.create_ship(self.root, "cargo_pod_generic", self.selected_item.parent.rigidbody.x, self.selected_item.parent.rigidbody.y, 1,1)
									)
								self.root.state_manager.states["game"].entities[-1].pick_up(self.selected_item)
								del self.selected_item.parent.inventory[self.selected_item.parent.inventory.index(self.selected_item)]
								self.first_start()
							else:
								ui_states.interdict_ok(self.root, title="Error", text="Cannot drop equipped item!%nDequip with X first", button = "OK")
						elif not self.shop_editable:
							ui_states.interdict_ok(self.root, title="Error", text="Not Editable", button = "OK")
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Not yours!", button = "OK")
					if event.key==pygame.K_u:
						if self.selected_item_is_owned and self.shop_editable:
							self.selected_item.fire()
						elif not self.shop_editable:
							ui_states.interdict_ok(self.root, title="Error", text="Not Editable", button = "OK")
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Not yours!", button = "OK")
					if event.key==pygame.K_e:
						if self.selected_item_is_owned and self.shop_editable:
							self.root.state_manager.start_interdicting("hardpoint_select", {
								"inv_id":self.sm_id,
								"item":self.selected_item
							})
						elif not self.shop_editable:
							ui_states.interdict_ok(self.root, title="Error", text="Not Editable", button = "OK")
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Not yours!", button = "OK")
					if event.key==pygame.K_s:
						if self.shop_editable:
							if self.selected_item.equipped==-1:
								self.selected_item.parent.try_stack(self.selected_item)
								self.first_start()
							else:
								ui_states.interdict_ok(self.root, title="Error", text="Dequip first", button = "OK")
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Not Editable", button = "OK")
					if event.key==pygame.K_a:
						if self.shop_editable:
							text=inputbox.ask(self.root.screen.screen, "Number to take >> ")
							if text=="meme man 2k14" and self.selected_item.id_str=="money":
								self.ship.inventory.append(item.create_item(absroot, "moneygun", self.ship))
								self.first_start()
								critical("Paul Blart Mode Enabled")
							try:
								self.selected_item.parent.try_split(self.selected_item,
								int(text)
								)
							except AssertionError as e:
								ui_states.interdict_ok(absroot, title="Failure", text=str(e), button = "OK")
							self.first_start()
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Not Editable", button = "OK")
					if event.key==pygame.K_t and self.is_shop:
						if self.selected_item_is_owned and self.shop_editable:
							if overlaps(self.selected_item.tags, self.shop_other.config.get("buys", ["_all"])) and self.selected_item.can_sell:
								cost=self.selected_item.get_cost()*absroot.galaxy.get_sector().get_sell_price(self.selected_item)
								def _yes(*a,**k):
									self.shop_other.pick_up(self.selected_item)
									del self.selected_item.parent.inventory[self.selected_item.parent.inventory.index(self.selected_item)]
									self.selected_item.reparent(self.shop_other)
									
									
									self.ship.inventory.append(item.create_item(absroot, "money", self.ship))
									self.ship.inventory[-1].count=cost
									self.ship.try_stack(self.ship.inventory[-1])
									self.selected_item=None
									self.first_start()
								if absroot.settings["gameplay"]["buysell_confirm"]:
									ui_states.interdict_yn(self.root, title="Confirm", text="Are you sure you want to sell "+str(self.selected_item.count)+" "+self.selected_item.name+" for "+str(cost),
									 button_y = "SELL", button_n="NO", callback_y=_yes)
								else:
									_yes()
							elif not self.selected_item.can_sell:
								ui_states.interdict_ok(self.root, title="Sorry...", text="You can't sell that", button = "OK")
							else:
								ui_states.interdict_ok(self.root, title="Sorry...", text="I don't buy that", button = "OK")

						elif not self.shop_editable:
							ui_states.interdict_ok(self.root, title="Error", text="Not Editable", button = "OK")
						else:
							if self.selected_item.can_buy:
								if self.ship.get_item("money"):
									cost=self.selected_item.get_cost()*absroot.galaxy.get_sector().get_buy_price(self.selected_item)
									if self.ship.get_item("money").count>cost:
										def _yes(*a, **k):
											self.ship.pick_up(self.selected_item)

											del self.selected_item.parent.inventory[self.selected_item.parent.inventory.index(self.selected_item)]
											
											self.selected_item.reparent(self.ship)
											
											self.ship.get_item("money").consume(cost)
											self.first_start()
											self.selected_item=None
										if absroot.settings["gameplay"]["buysell_confirm"]:
											ui_states.interdict_yn(self.root, title="Confirm", text="Are you sure you want to buy "+str(self.selected_item.count)+" "+self.selected_item.name+" for "+str(cost),
								 			 button_y = "BUY", button_n="NO", callback_y=_yes)
										else:
											_yes()
									else:
										ui_states.interdict_ok(self.root, title="Sorry...", text="You don't have enough money.%nNeed "+str(cost), button = "OK")
								else:
									ui_states.interdict_ok(self.root, title="Sorry...", text="You don't even have 1 money!", button = "OK")
							else:
								ui_states.interdict_ok(self.root, title="Sorry...", text="You can't buy that", button = "OK")

			if event.type==pygame.MOUSEBUTTONDOWN:
				adj_pos=list(pygame.mouse.get_pos())
				#adj_pos[1]+=self.OFFSET
				if event.button==1:	
					for l in self.tiles:
						if l[1].collidepoint(adj_pos):
							self.selected_item=l[0]
							self.selected_item_is_owned=l[3]
				if event.button==4:
					for l in self.tiles:
						l[1].move_ip(0,64)
					self.initial_offset+=64
				if event.button==5:
					for l in self.tiles:
						l[1].move_ip(0,-64)
					self.initial_offset-=64
