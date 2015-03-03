import absroot, pygame, tasks, textwrap

class GenericTooltipMixin(object):
	tt_image=None
	tt_islive=False
	def tt_needs_rerender(self):
		return self.tt_islive

	def tt_render_image(self):
		raise NotImplementedError()

	def tt_image_init(self, size):
		self.tt_image=pygame.Surface(size).convert_alpha()
		self.tt_image.fill((0,0,0,0))

	def tt_image_clip(self, bonus=(5,5,5,5)):
		temp_image=self.tt_image
		self.tt_image=pygame.Surface((temp_image.get_bounding_rect().width+bonus[0]+bonus[2], temp_image.get_bounding_rect().height+bonus[1]+bonus[3])).convert_alpha()
		self.tt_image.fill((0,0,0,0))
		self.tt_image.blit(temp_image, (bonus[0], bonus[1]))

	def tt_add_box(self, color=(127,127,127), border=(200,200,200), bordersize=3):
		image=pygame.Surface(self.tt_image.get_size())
		image.fill(color)
		pygame.draw.rect(image, border, pygame.Rect((0,0), image.get_size()), bordersize)
		image.blit(self.tt_image, (0,0))
		self.tt_image=image

	def tt_update_image(self):
		if self.tt_needs_rerender() or (self.tt_image is None):
			self.tt_render_image()

	def tt_draw(self, pos):
		self.tt_update_image()
		
		rect=pygame.Rect(pos, self.tt_image.get_size())
		rect.bottom -= max(rect.bottom-absroot.renderspace_size[1],0)
		rect.right -= max(rect.right-absroot.renderspace_size[0],0)

		absroot.screen.screen.blit(self.tt_image, rect)

	def tt_update(self, rect):
		if rect.collidepoint(pygame.mouse.get_pos()):
			self.tt_draw(pygame.mouse.get_pos())

	def tt_delay_update(self, rect):
		def _temp():
			self.tt_update(rect)
		tasks.delay( _temp , 'tooltips' )

def render_wrapped_text(text, width, font, color=(255,255,255)):
	chars=width/font.size("_")[0]
	wrapped=[]
	#print text
	for i in text.split("\n"):
		wrapped.extend(textwrap.wrap(i, chars))
	height=len(wrapped)*font.size("|")[1]
	surf=pygame.Surface((width, height)).convert_alpha()
	surf.fill((0,0,0,0))
	pos=0
	for line in wrapped:
		surf.blit(font.render(line.replace("\n","").replace("\r",""), 1, color), (0, pos))
		pos+=font.size("|")[1]
	return surf