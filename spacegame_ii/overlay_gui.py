import pygame
from rotutil import rot_center, get_rel_angle, get_angle
from logging import debug, info, warning, error, critical

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

class IngameRenderedConsole:
	#Line tuple is (text, color, bgcolor, bold, italics, underline)
	def __init__(self, root, lines=10):
		self.root=root
		self.lines=[]
		self.enabled=True
		self.debug=False
		self.maxlines=lines

		self.post("Console Started", (0,255,0))

	def enable(self):
		self.enabled=True

	def disable(self):
		self.enabled=False

	def enable_debug(self):
		self.debug=True

	def disable_debug(self):
		self.debug=False

	def render_line(self, line, offset):
		self.root.gamedb("font_sys_mono").set_bold(line[3])
		self.root.gamedb("font_sys_mono").set_italic(line[4])
		self.root.gamedb("font_sys_mono").set_underline(line[5])
		self.root.screen.screen.blit(self.root.gamedb("font_sys_mono_13").render(
				line[0], False, pygame.Color(*line[1]), pygame.Color(*line[2])
			)
		, offset)
		self.root.gamedb("font_sys_mono").set_bold(False)
		self.root.gamedb("font_sys_mono").set_italic(False)
		self.root.gamedb("font_sys_mono").set_underline(False)

	def render(self, position):
		position=list(position)
		pygame.draw.rect(self.root.screen.screen, (0,0,0), pygame.Rect(
			position,
			(self.root.gamedb("font_sys_mono_13").size("A")[0]*50,
			self.root.gamedb("font_sys_mono_13").size("A")[1]*self.maxlines)
			)
		)
		pygame.draw.rect(self.root.screen.screen, (255,255,255), pygame.Rect(
			position[0]-2,
			position[1]-2,
			self.root.gamedb("font_sys_mono_13").size("A")[0]*50,
			self.root.gamedb("font_sys_mono_13").size("A")[1]*self.maxlines
			),
			3
		)
		if self.enabled:
			for l in reversed(self.lines):
				self.render_line(l, position)
				position[1]+=self.root.gamedb("font_sys_mono_13").size(l[0])[1]

	def post(self, text, color=(255,255,255,255), bg=(0,0,0,0), bold=False, italic=False, underline=False, debugmsg=False):
		debug("Posting message: "+text)
		if not debugmsg or self.debug:
			debug("Message posted")
			self.lines.append((text, color, bg, bold, italic, underline))
			if len(self.lines)>self.maxlines:
				del self.lines[0]
		else:
			debug("Policy did not allow for message posting")