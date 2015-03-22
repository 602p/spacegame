import state, absroot, pygame, ui_states, item
import logging, uidict, quests, random, tooltips
module_logger=logging.getLogger("sg.plgissc.bar")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

class BarPatron(tooltips.ReloadOnMouseOverTooltipMixin):
	classfancyname=""
	def __init__(self, pos, race=None, image=None):
		
		self.image=image
		if image is None:
			#print "IIN"
			self.faction_o=absroot.faction_manager.pick_faction_with_tag("species")
			self.image=random.choice(self.faction_o.config["people_pool"])

			self.name=self.faction_o.gen_name()

		self.image_o=absroot.gamedb(self.image)
		
		self.pos=pos
		#self.race_o=pick_faction_with_tag
		self.rect=pygame.Rect(pos, self.image_o.get_size())
		self.player_relations="N/A"
		self.id_string="BARPATRON_???"
		self._init()

	def _init(s):pass

	def render(self):
		absroot.screen.screen.blit(self.image_o, self.pos)
		#

	def save_to_config_node(self):
		o = {
			"name":self.name,
			"image":self.image,
			"pos":self.pos,
			"_class":type(self).__name__
		}
		o.update(self._save_to_config_node())
		return o

	@staticmethod
	def load_from_config_node(node):
		o = eval(node["_class"])(
			node["pos"],
			image=node["image"]
		)
		o.name=node["name"]
		o._load_from_config_node(node)
		return o

	def _load_from_config_node(s,n):pass
	def _save_to_config_node(s):return {}
	def on_click(self):pass

	def tt_render_image(self):
		self.tt_image_init((1000,1000))

		self.tt_image.blit(absroot.gamedb("font_item_title").render(self.name, 1, (20,20,20)), (0,0))
		self.tt_image.blit(
			absroot.gamedb("font_item_desc").render(type(self).classfancyname, 1, (20,20,20)),
			(0,absroot.gamedb("font_item_title").size("|")[1]))
		if self.get_additional_text():
			self.tt_image.blit(
				absroot.gamedb("font_item_desc").render(self.get_additional_text(), 1, (20,20,20)),
				(0,absroot.gamedb("font_item_title").size("|")[1]+absroot.gamedb("font_item_desc").size("|")[1]))

		self.tt_image_clip()
		self.tt_add_box()

	def get_additional_text(self):
		return ""

class ChatPatron(BarPatron):
	classfancyname="Just wants to chat..."
	def on_click(self):
		absroot.dialog_manager.start_dialog(
			self,
			"bar_greeting"
		)
	def get_faction_attr(self, _, d="[[Do not use get_faction_attr on BarPatrons]]"):
		return d
		#

class BuyPatron(BarPatron):
	classfancyname="Wants to buy something..."
	def _init(self):
		self.wanted=random.choice([x for x in absroot.item_factories.keys() if absroot.item_factories[x].questable_for])
		self.wanted_o=absroot.item_factories[self.wanted]
		self.wanted_count=random.randint(1,20)
		self.payout=random.uniform(1.1,1.6)
		self.done=False

	def on_click(self):
		if not self.done:
			found=False
			for i in absroot.gamestate.player.inventory:
				if i.id_str==self.wanted:
					if i.count>=self.wanted_count:
						def callback_y(s):
							i.consume(self.wanted_count)
							i.parent.inventory.append(item.create_item2("money", i.parent, count=self.payout*self.wanted_o.cost*self.wanted_count))
							ui_states.interdict_ok2("Request", "Thank you!%nI've payed you, and taken the items from your inventory.", button="Goodbye")
							self.done=True
						def callback_n(s):
							ui_states.interdict_ok2("Request", "To bad...", button="Goodbye")
						ui_states.interdict_yn2("Deal", "Will you sell me "+str(self.wanted_count)+" "+self.wanted_o.name+"(s) for "+str(self.payout*self.wanted_o.cost*self.wanted_count)+"Cr?", button_y="YES", button_n="NO", callback_y=callback_y, callback_n=callback_n)
						ui_states.interdict_ok2("Request", "Looks like you've got it...", button="Let's negotiate...")
						found=True
			if not found:
				ui_states.interdict_ok2("Request", "Looks like you don't have it...%n(Make sure that they are all in a stack)", button="I'll come back later")

			#Cover popup goes last
			ui_states.interdict_ok2("Request", "I'm looking for "+str(self.wanted_count)+" "+self.wanted_o.name+"(s)...%nI'll give you "+str(self.payout*self.wanted_o.cost*self.wanted_count)+"Cr", button="OK")
		else:
			ui_states.interdict_ok2("Request", "We've already talked, thank you!", button="Goodbye")

	def _save_to_config_node(s):return {"reqitem":s.wanted, "reqcount":s.wanted_count, "payout":s.payout, "done":s.done}
	def _load_from_config_node(s, n):
		s.wanted=n["reqitem"]
		s.wanted_o=absroot.item_factories[s.wanted]
		s.wanted_count=n["reqcount"]
		s.payout=n["payout"]
		s.done=n["done"]

	def get_additional_text(self):
		return "(You've completed his task)" if self.done else ""

class SellPatron(BarPatron):
	classfancyname="Wants to sell something..."
	def _init(self):
		self.selling=random.choice([x for x in absroot.item_factories.keys() if absroot.item_factories[x].questable_for])
		self.selling_o=absroot.item_factories[self.selling]
		self.selling_count=random.randint(1,20)
		self.cost_mod=random.uniform(1.1,1.6)
		self.done=False
		self.fcost=self.cost_mod*self.selling_o.cost*self.selling_count

	def on_click(self):
		if not self.done:
			found=False
			for i in absroot.gamestate.player.inventory:
				if i.id_str=="money":
					if i.count>=self.fcost:
						def callback_y(s):
							i.consume(self.fcost)
							i.parent.inventory.append(item.create_item2(self.selling, i.parent, count=self.selling_count))
							ui_states.interdict_ok2("Selling", "Thank you!%nI've charged you, and addied the items to your inventory.", button="Goodbye")
							self.done=True
						def callback_n(s):
							ui_states.interdict_ok2("Selling", "To bad...", button="Goodbye")
						ui_states.interdict_yn2("Deal", "Will you buy "+str(self.selling_count)+" "+self.selling_o.name+"(s) for "+str(self.fcost)+"Cr?", button_y="YES", button_n="NO", callback_y=callback_y, callback_n=callback_n)
						ui_states.interdict_ok2("Selling", "You've got the cash...", button="Let's negotiate...")
						found=True
			if not found:
				ui_states.interdict_ok2("Selling", "You don't have enough money!%n(Make sure it's stacked)", button="I'll come back later")

			#Cover popup goes last
			ui_states.interdict_ok2("Selling", "I'm selling "+str(self.selling_count)+" "+self.selling_o.name+"(s)... for "+str(self.fcost)+"Cr", button="OK")
		else:
			ui_states.interdict_ok2("Selling", "We've already talked, thank you!", button="Goodbye")

	#def _save_to_config_node(s):return {"reqitem":s.wanted, "reqcount":s.selling_count, "payout":s.payout, "done":s.done}

	def _save_to_config_node(s):return {"sellitem":s.selling, "sellcount":s.selling_count, "cost_mod":s.cost_mod, "done":s.done}
	def _load_from_config_node(s, n):
		s.selling=n["sellitem"]
		s.selling_o=absroot.item_factories[s.selling]
		s.selling_count=n["sellcount"]
		s.cost_mod=n["cost_mod"]
		s.done=n["done"]
		s.fcost=s.cost_mod*s.selling_o.cost*s.selling_count

	def get_additional_text(self):
		return "(You've completed his task)" if self.done else ""

class QuestPatron(BarPatron):
	classfancyname="Has a job for you..."
	def _init(self):
		self.qid=random.choice(absroot.gamedb("cfg_list_bar_pquests"))
		self.quest=quests.create_quest2(self.qid)
		debug("Created a QuestPatron for "+self.qid)
		self.done=False

	def on_click(self):
		if not self.done:
			def _y(*a):
				absroot.quest_manager.add_quest(self.quest)
				ui_states.interdict_ok2("Quest", "Thank you very much", button="Goodbye")
				self.done=True
			ui_states.interdict_yn2("Quest", "Are you interested?", button_y="YES", button_n="NO",
				callback_y=_y,
				callback_n=lambda s:ui_states.interdict_ok2("Quest", "I'm sorry to hear that...", button="Goodbye"))
			ui_states.interdict_ok2("Quest", "Here's what I have in mind...%n("+self.qid+"):%n "+self.quest.get_description(), button="...")
			ui_states.interdict_ok2("Quest", "I have a buiness proposition for you....", button="Let's hear it")
		else:
			ui_states.interdict_ok2("Quest", "Thank you for taking me up on it!", button="Goodbye")

	def _save_to_config_node(self):return {"quest":self.quest.save_to_config_node(), "done":self.done}
	def _load_from_config_node(self, n):
		self.quest = quests.create_quest2(n["quest"]["id"])
		self.quest.do_additional_load(n["quest"])
		self.done = n["done"]

	def get_additional_text(self):
		return "(You've completed his task)" if self.done else ""

patron_types=[ChatPatron, BuyPatron, SellPatron, QuestPatron]

class BarState(state.InterdictingState):
	def first_start(self):
		debug("Starting BarState")
		self.g_config=self.params[0]
		self.config=self.params[2]
		#print self.config
		self.ship=self.params[1]
		self.channel=pygame.mixer.Channel(1)
		self.channel.play(absroot.gamedb(self.config.get("ambiance", "snd_quarks_bar_ambiance")), -1)
		self.title_render=absroot.gamedb(self.g_config.get("lg_font", "font_standard_large")).render(self.g_config.get("name","[Station name not set]")+" Bar", 1, self.config.get("color",(255,255,255)))

		self.people=[]

		if "bar_people" in self.ship.database:
			for conf in self.ship.database["bar_people"]:
				self.people.append(BarPatron.load_from_config_node(conf))
		else:
			for _ in xrange(random.randint(self.config.get("patron_count_min", 3), self.config.get("patron_count_min", 10))):
				self.people.append(random.sample(patron_types,1)[0]( 
					(
						random.randint(0, 800),
						random.randint(0, 600)
					),
					race=absroot.faction_manager.pick_faction_with_tag("species")
				))

	def internal_update(self):
		absroot.screen.screen.blit(absroot.gamedb(self.config.get("scn_image", "large_black_bg")), (0,0))
		absroot.screen.screen.blit(self.title_render, (0,0))

		for patron in self.people:
			patron.render()
			pygame.draw.rect(absroot.screen.screen, (255,0,0), patron.rect, 2)
			patron.tt_delay_update(patron.rect)

	def process_events(self, events):
		for event in events:
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.finish()
			if event.type==pygame.MOUSEBUTTONDOWN:
				if event.button==1:
					for patron in self.people:
						if patron.rect.collidepoint(pygame.mouse.get_pos()):
							patron.on_click()

	def suspend(self):
		self.channel.stop()
		self.ship.database["bar_people"]=[]
		for person in self.people:
			self.ship.database["bar_people"].append(person.save_to_config_node())

def init_states(root, console):
	info("Setting up BarState")
	root.state_manager.factories["icn_ss_bar"]=state.InterdictingStateFactory(BarState)