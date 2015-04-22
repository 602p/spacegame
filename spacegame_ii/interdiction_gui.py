import pygame, textwrap
from logging import debug, info, warning, error, critical
import logging, tasks
module_logger=logging.getLogger("sg.interdiction_gui")
debug, info, warn, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def interdict_ok(root, title, content, button="ACCEPT", titlecolor=(255,255,255), textcolor=(0,0,0), buttoncolor=(0,0,255)):
	tasks.display_hanging_message("Something started interdict_ok, Don't use that!", color=(255,255,0))
	debug("Starting interdict_ok")
	warn("THIS MODULE IS DEPRECATED. USE UI_STATES INSTEAD")
	debug("T:"+title)
	debug("C:"+content)
	debug("B:"+button)
	screen=root.screen.screen
	x=350
	y=150
	gamedb=root.gamedb

	width=600
	offset=20

	wrapped=textwrap.wrap(content, 48)
	titlerender=gamedb.get_asset("font_standard_large").render(title, 1, titlecolor)
	buttonrender=gamedb.get_asset("font_standard_large").render(button, 1, buttoncolor)	

	screen.blit(gamedb.get_asset("uia_ok_dialog"), (x,y))
	screen.blit(titlerender, (x+5,y+30))
	screen.blit(buttonrender, (x+58,y+314))

	ok_collide=pygame.Rect(x+25, y+308, 170, 50)#pylygon.polygon.Polygon([(x+25,y+308), (x+191, y+308), (x+191,y+356), (x+72, y+356)])
	#pygame.draw.rect(screen, (255,0,0), ok_collide.get_rect())

	i=y+60
	for l in wrapped:
		line=gamedb.get_asset("font_sys_mono").render(l, 1, textcolor)
		try:
			screen.blit(line, (x+5,i))
		except TypeError: pass
		i+=20

	run=1
	while not pygame.QUIT in [e.type for e in pygame.event.get()] and run:
		if pygame.mouse.get_pressed()[0]:
			if ok_collide.collidepoint(pygame.mouse.get_pos()):
				return True
		root.clock.tick()
		pygame.display.flip()

def interdict_yn(root, title, content, buttont="YES", buttonf="NO", titlecolor=(255,255,255), textcolor=(0,0,0), buttoncolort=(0,0,255), buttoncolorf=(0,0,255)):
	tasks.display_hanging_message("Something used interdict_yn, Don't use that!", color=(255,255,0))
	debug("Starting interdict_yn")
	warn("THIS MODULE IS DEPRECATED. USE UI_STATES INSTEAD")
	debug("T:"+title)
	debug("C:"+content)
	debug("BT:"+buttont)
	debug("BF:"+buttonf)
	screen=root.screen.screen
	x=350
	y=150
	gamedb=root.gamedb

	width=600
	offset=20

	wrapped=textwrap.wrap(content, 48)
	titlerender=gamedb.get_asset("font_standard_large").render(title, 1, titlecolor)
	buttonrendert=gamedb.get_asset("font_standard_large").render(buttont, 1, buttoncolort)	
	buttonrenderf=gamedb.get_asset("font_standard_large").render(buttonf, 1, buttoncolorf)	

	screen.blit(gamedb.get_asset("uia_yn_dialog"), (x,y))
	screen.blit(titlerender, (x+5,y+30))
	screen.blit(buttonrendert, (x+58,y+314))
	screen.blit(buttonrenderf, (x+406,y+314))

	t_collide=pygame.Rect(x+25, y+308, 170, 50)#pylygon.polygon.Polygon([(x+25,y+308), (x+191, y+308), (x+191,y+356), (x+72, y+356)])
	f_collide=pygame.Rect(x+404, y+308, 170, 50)

	i=y+60
	for l in wrapped:
		line=gamedb.get_asset("font_sys_mono").render(l, 1, textcolor)
		try:
			screen.blit(line, (x+5,i))
		except TypeError: pass
		i+=20

	run=1
	while not pygame.QUIT in [e.type for e in pygame.event.get()] and run:
		if pygame.mouse.get_pressed()[0]:
			if t_collide.collidepoint(pygame.mouse.get_pos()):
				return True
			if f_collide.collidepoint(pygame.mouse.get_pos()):
				return False
		root.clock.tick()
		pygame.display.flip()
