import pygame, state, inputbox, ship, ui_states
from logging import debug, info, warning, error, critical
import logging
module_logger=logging.getLogger("sg.inventory")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


class InventoryState(state.InterdictingState):
	def first_start(self):
		debug("Starting inventory state")
		self.ship=self.params
		self.font=self.root.gamedb("font_inventory_default")
		self.font_lg=self.root.gamedb("font_inventory_large")
		self.config=self.root.gamedb("cfg_inventory_box")
		self.image=self.root.gamedb("uia_inventory_box")
		self.name_pos=self.config["ship_name_pos"]
		self.mass_pos=self.config["mass_pos"]
		self.item_pos=self.config["items_pos"]
		self.selected_item=None

		debug("Building rects/images...")
		self.cache_items=[]
		currpos=[x for x in self.item_pos]
		for item in self.ship.inventory:
			image=pygame.Surface((1500,1500)).convert_alpha()
			image.fill((0,0,0,0))
			pos=[0,0]
			for line in item.get_desc_text():
				image.blit(self.font.render(line, 1, (255,255,255)), pos)
				pos[1]+=self.font.size("|")[1]
			
			rect=pygame.Rect(currpos[0]+64, currpos[1], image.get_size()[0], 64)

			pygame.draw.rect(image, (0,255,0), pygame.Rect(-2,0,1300,63), 2)

			self.cache_items.append([image, item.get_inventory_image(), rect, item])
			currpos[0]=self.item_pos[0]
			currpos[1]+=64

	def internal_update(self):
		screen=self.root.screen.screen
		screen.blit(self.image, (0,0))
		screen.blit(self.font_lg.render(self.ship.name, 1, (0,0,255)), self.name_pos)
		screen.blit(self.font_lg.render(str(self.ship.get_inventory_mass())+"/"+str(self.ship.cargo), 1, (0,0,255)), self.mass_pos)

		for text_image, inv_image, rect, item in self.cache_items:
			if item==self.selected_item:
				pygame.draw.rect(screen, pygame.Color(0,0,255,127), pygame.Rect(rect.topleft, (10000, 64)))
			screen.blit(inv_image, (rect.left-64, rect.top))
			screen.blit(text_image, rect.topleft)
			item.tt_delay_update(rect)
			item.tt_delay_update(pygame.Rect((rect.left-64, rect.top), (64,64)))

			
	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
				if self.selected_item:
					if event.key==pygame.K_x:
						self.selected_item.dequip()
						self.first_start()
					if event.key==pygame.K_d:
						if self.selected_item.equipped==-1:
							self.root.state_manager.states["game"].entities.append(
								ship.create_ship(self.root, "cargo_pod_generic", self.selected_item.parent.rigidbody.x, self.selected_item.parent.rigidbody.y, 1,1)
								)
							self.root.state_manager.states["game"].entities[-1].pick_up(self.selected_item)
							del self.selected_item.parent.inventory[self.selected_item.parent.inventory.index(self.selected_item)]
							self.first_start()
						else:
							ui_states.interdict_ok(self.root, title="Error", text="Cannot drop equipped item!%nDequip with X first", button = "OK")

					if event.key==pygame.K_u:
						self.selected_item.fire()
					if event.key==pygame.K_e:
						self.root.state_manager.start_interdicting("hardpoint_select", {
							"inv_id":self.sm_id,
							"item":self.selected_item
						})
					if event.key==pygame.K_s:
						self.selected_item.parent.try_stack(self.selected_item)
						self.first_start()
					if event.key==pygame.K_a:
						self.selected_item.parent.try_split(self.selected_item,
							int(inputbox.ask(self.root.screen.screen, "Number to take >> "))
							)
						self.first_start()

			if event.type==pygame.MOUSEBUTTONDOWN:
				for _,_,rect,item in self.cache_items:
					if rect.collidepoint(pygame.mouse.get_pos()):
						self.selected_item=item

class SlotSelectorState(state.InterdictingState):
	def first_start(self):
		self.font=self.root.gamedb("font_inventory_large")
		self.cache_hp=[]
		self.selected_hp=None
		self.filled=[]

		cpos=[0,0]
		idx=0
		for hardpoint in self.params["item"].parent.hardpoints:
			filledc=0
			if self.params["item"].parent.get_item_in_hardpoint(idx):
				self.filled.append(idx)
				filledc=1
			t="Hardpoint of type <"+hardpoint["size"]+"> at "+str(hardpoint["x"])+","+str(hardpoint["y"])
			if filledc:
				t+=" (FULL)"
			image=self.font.render(t, 1, (127,127,127) if filledc else (255,255,255))
			rect=pygame.Rect(cpos, image.get_size())
			self.cache_hp.append([image, rect, idx])
			idx+=1
			cpos[1]+=self.font.size("|")[1]
			cpos[0]=0

	def internal_update(self):
		screen=self.root.screen.screen
		screen.fill((0,0,0))

		for image, rect, idx in self.cache_hp:
			if idx==self.selected_hp:
				pygame.draw.rect(screen, pygame.Color(0,0,255,127), pygame.Rect(rect.topleft, (10000, rect.height)))
			screen.blit(image, rect)

	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
				if self.selected_hp!=-1 and self.selected_hp!=None:
					if self.selected_hp not in self.filled:
						if event.key==pygame.K_RETURN:
							self.params["item"].equip(self.selected_hp)
							self.finish()
			if event.type==pygame.MOUSEBUTTONDOWN:
				for image, rect, idx in self.cache_hp:
					if rect.collidepoint(pygame.mouse.get_pos()):
						self.selected_hp=idx

	def suspend(self):
		self.root.state_manager.states[self.params["inv_id"]].first_start()