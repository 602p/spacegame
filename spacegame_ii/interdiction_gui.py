import pygame, textwrap, pylygon
from logging import debug, info, warning, error, critical

def interdict_ok(root, title, content, button="ACCEPT", titlecolor=(255,255,255), textcolor=(0,0,0), buttoncolor=(0,0,255)):
	debug("Starting interdict_ok")
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

	ok_collide=pylygon.polygon.Polygon([(x+25,y+308), (x+191, y+308), (x+191,y+356), (x+72, y+356)])
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
				return
		root.clock.tick()
		pygame.display.flip()
