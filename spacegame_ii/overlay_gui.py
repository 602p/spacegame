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
			screen.blit(e.get_inventory_image(), (x+xo, y+2))
		if pygame.mouse.get_pressed()[0] and pygame.Rect(x+xo, y+2, 64, 64).collidepoint(pygame.mouse.get_pos()):
			ship.selected_wep=ship.hardpoints.index(i)
		xo+=64

	for i in xrange(0,13):
		xo=i*64
		pygame.draw.line(screen, (255,0,0), (x+xo+64, y+2), (x+xo+64, y+64), 2)

	pygame.draw.rect(screen, (255,0,0), pygame.Rect(x,y,898,67), 2)
	
	if ship.get_item_in_hardpoint(ship.selected_wep)!=None:
		screen.blit(root.gamedb("font_sys_mono_13").render(ship.get_item_in_hardpoint(ship.selected_wep).name, 0, (0,255,0)),
			(x+(ship.selected_wep*64),y-16))
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
	def __init__(self, root, lines=10, width=50, font="font_sys_mono_13"):
		self.root=root
		self.lines=[]
		self.enabled=True
		self.debug=False
		self.maxlines=lines
		self.width=width
		self.font=font
		self.debug_to_console=False

		#self.post("Console Started")

	def enable(self):
		self.enabled=True

	def disable(self):
		self.enabled=False

	def enable_debug(self):
		self.debug=True

	def disable_debug(self):
		self.debug=False

	def render_line(self, line, offset):
		f=self.root.gamedb(self.font)
		f.set_bold(line[3])
		f.set_italic(line[4])
		f.set_underline(line[5])
		self.root.screen.screen.blit(f.render(
				line[0], False, pygame.Color(*line[1]), pygame.Color(*line[2])
			)
		, offset)
		f.set_bold(False)
		f.set_italic(False)
		f.set_underline(False)

	def render(self, position):
		position=list(position)
		pygame.draw.rect(self.root.screen.screen, (0,0,0), pygame.Rect(
			position,
			(self.root.gamedb(self.font).size("A")[0]*self.width,
			self.root.gamedb(self.font).size("A")[1]*self.maxlines)
			)
		)
		pygame.draw.rect(self.root.screen.screen, (255,255,255), pygame.Rect(
			position[0]-2,
			position[1]-2,
			self.root.gamedb(self.font).size("A")[0]*self.width,
			self.root.gamedb(self.font).size("A")[1]*self.maxlines+4
			),
			3
		)
		if self.enabled:
			for l in self.lines:
				self.render_line(l, position)
				position[1]+=self.root.gamedb(self.font).size(l[0])[1]

	def post(self, text, color=(255,255,255,255), bg=(0,0,0,0), bold=False, italic=False, underline=False, debugmsg=False):
		if self.debug_to_console:debug("Posting message: "+text)
		if not debugmsg or self.debug:
			if self.debug_to_console:debug("Message posted")
			self.lines.append((text, color, bg, bold, italic, underline))
			if len(self.lines)>self.maxlines:
				del self.lines[0]
		else:
			if self.debug_to_console:debug("Policy did not allow for message posting")

	def postd(self, cfg, formatter):
		self.post(
			formatter.format_string(cfg.get("text", "")),
			cfg.get("color", (255,255,255,255)),
			cfg.get("bg", (0,0,0)),
			cfg.get("bold", False),
			cfg.get("italic", False),
			cfg.get("underline", False),
			cfg.get("debug", False)
		)