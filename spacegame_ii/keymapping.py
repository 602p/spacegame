import pygame, json, state
import logging
module_logger=logging.getLogger("sg.keymapping")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def _load_mapping(path):
	with open(path, 'r') as fd:
		return json.load(fd)

def load_mapping(path):
	return _load_mapping(path)["mapping"]

def save_mapping(path, mapping):
	old_mapping=_load_mapping(path)
	new_dict={"mapping":mapping}
	new_dict["naming"]=old_mapping["naming"]
	new_dict["project_name"]=old_mapping["project_name"]
	with open(path, 'w') as fd:
		json.dump(new_dict, fd, indent=4)

class KeyMapperState(state.InterdictingState):
	def first_start(self):
		self.font=pygame.sysfont.SysFont('monospace', 20)
		self.font.set_bold(1)
		self.mapping=self.root.settings["keybindings"]
		self.naming =_load_mapping(self.root.settings["keymapping_file"])["naming"]
		self.current_key=0
		self.captured_id=-1
		self.captured_name=""
		self.state="capture"
	def internal_update(self):
		screen=self.root.screen.screen
		screen.fill((0,0,0))
		if self.state=="capture":
			screen.blit(self.font.render("Press key to bind to: ", 1, (255,255,255)), (0,0))
			screen.blit(self.font.render(self.naming[self.naming.keys()[self.current_key]], 0, (0,255,0)), (300,0))
			if self.captured_id==-1:
				screen.blit(self.font.render("Waiting...", 0, (255,255,255)), (0,40))
			else:
				screen.blit(self.font.render("Captured DEC:"+str(self.captured_id)+" HEX:"+str(hex(self.captured_id))+" NAME:"+self.captured_name+" (click for next)", 1, (0,255,0)),(0,40))
		else:
			screen.blit(self.font.render("All keys captured...", 0, (255,255,255)), (0,0))
			screen.blit(self.font.render("Click to close", 0, (255,255,255)), (0,40))
		self.root.fps=999999
	def process_events(self, events):
		#print self.state
		for event in events:
			if event.type==pygame.QUIT:
				self.running=0
			if event.type==pygame.MOUSEBUTTONDOWN:
				if self.state=="capture" and self.captured_id!=-1:
					self.mapping[self.mapping.keys()[self.current_key]]=self.captured_id
					self.current_key+=1
					self.captured_id=-1
					self.captured_name=""
					if self.current_key==len(self.mapping):
						self.state="show_exit"
				elif self.state=="show_exit":
					#print "finishing..."
					self.finish(None)
			if event.type==pygame.KEYDOWN:
				self.captured_id=event.key
				try:
					self.captured_name=event.unicode
				except AttributeError:
					self.captured_name="(N/A)"
	def suspend(self):
		save_mapping(self.root.settings["keymapping_file"],self.mapping)

if __name__=="__main__":
	pygame.init()
	font=pygame.sysfont.SysFont('monospace', 20)
	font.set_bold(1)
	screen=pygame.display.set_mode((800,60))
	pygame.display.set_caption(_load_mapping()["project_name"])
	mapping=load_mapping()
	naming =_load_mapping()["naming"]
	current_key=0
	captured_id=-1
	captured_name=""
	state="capture"

	running=1
	while running:
		screen.fill((0,0,0))
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				running=0
			if event.type==pygame.MOUSEBUTTONDOWN:
				if state=="capture" and captured_id!=-1:
					mapping[mapping.keys()[current_key]]=captured_id
					current_key+=1
					captured_id=-1
					captured_name=""
					if current_key==len(mapping):
						state="show_exit"
				elif state=="show_exit":
					running=0
			if event.type==pygame.KEYDOWN:
				captured_id=event.key
				try:
					captured_name=event.unicode
				except AttributeError:
					captured_name="(N/A)"
		if state=="capture":
			screen.blit(font.render("Press key to bind to: ", 1, (255,255,255)), (0,0))
			screen.blit(font.render(naming[naming.keys()[current_key]], 0, (0,255,0)), (300,0))
			if captured_id==-1:
				screen.blit(font.render("Waiting...", 0, (255,255,255)), (0,40))
			else:
				screen.blit(font.render("Captured DEC:"+str(captured_id)+" HEX:"+str(hex(captured_id))+" NAME:"+captured_name+" (click for next)", 1, (0,255,0)),(0,40))
		else:
			screen.blit(font.render("All keys captured...", 0, (255,255,255)), (0,0))
			screen.blit(font.render("Click to close", 0, (255,255,255)), (0,40))
		pygame.display.flip()
	save_mapping(mapping)
	print "Mapping Saved"