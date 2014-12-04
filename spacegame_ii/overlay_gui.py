import pygame
from rotutil import rot_center, get_rel_angle, get_angle

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

def render_rangefinder(root, player, point, color='red'):
	gamedb=root.gamedb
	screen=root.screen

	image=gamedb('uio_arrow_transparent'+color+'_up').copy()

	delta_angle=get_rel_angle(get_angle(player.rotated_rect.center[0], point[0],
		player.rotated_rect.center[1], point[1]), 0)
	
	rotated_image, rotated_rect=rot_center(image, pygame.Rect(point, image.get_size()), delta_angle)

	rect=screen.clamp(rotated_rect)
	norender_rect=screen.screen.get_rect().copy()
	norender_rect.move_ip(2,2)
	norender_rect.width-=2
	norender_rect.height-=2
	if not norender_rect.collidepoint(rect.x, rect.y):
		screen.screen.blit(rotated_image, rect)