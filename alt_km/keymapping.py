import pygame, json

MAPPING_FILE="keymapping.json"

def _load_mapping():
	with open(MAPPING_FILE, 'r') as fd:
		return json.load(fd)

def load_mapping():
	return _load_mapping()["mapping"]

def save_mapping(mapping={}):
	old_mapping=_load_mapping()
	new_dict={"mapping":mapping}
	new_dict["naming"]=old_mapping["naming"]
	new_dict["project_name"]=old_mapping["project_name"]
	with open(MAPPING_FILE, 'w') as fd:
		json.dump(new_dict, fd, indent=4)

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