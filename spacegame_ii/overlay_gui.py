import pygame


def render_wepbar(root, state, ship, x, y):
	screen=root.screen.screen
	pygame.draw.rect(screen, (128,128,128), pygame.Rect(x,y,898,68)) #14 slots
	xo=2

	for i in ship.hardpoints:
		e=ship.get_item_in_hardpoint(ship.hardpoints.index(i))
		if e:
			screen.blit(e.inventory_image, (x+xo, y+2))
		if pygame.mouse.get_pressed()[0] and pygame.Rect(x+xo, y+2, 64, 64).collidepoint(pygame.mouse.get_pos()):
			ship.selected_wep=ship.hardpoints.index(i)
		xo+=64

	for i in xrange(0,13):
		xo=i*64
		pygame.draw.line(screen, (255,0,0), (x+xo+64, y+2), (x+xo+64, y+64), 2)

	pygame.draw.rect(screen, (255,0,0), pygame.Rect(x,y,898,67), 2)
	pygame.draw.rect(screen, (0,255,0), pygame.Rect(x+(ship.selected_wep*64),y,64,66), 2)