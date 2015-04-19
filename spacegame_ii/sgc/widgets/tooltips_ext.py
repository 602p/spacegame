import sys
sys.path.append('../..') #DUMB HACK

import tooltips
import button
import absroot

class TTButton(button.Button, tooltips.ReloadOnMouseOverTooltipMixin):
	def update(self, dt):
		button.Button.update(self, dt)
		self.tt_delay_update(self.rect_abs)

class SimpleTTButton(TTButton):
	def _config(self, **kwargs):
		self.tt_title=kwargs["tt_title"]
		self.tt_body=kwargs.get("tt_body", "")
		TTButton._config(self, **kwargs)

	def tt_render_image(self):
		self.tt_image_init((500,500))

		self.tt_image.blit(absroot.gamedb("font_item_title").render(self.tt_title, 1, (20,20,20)), (0,0))
		if self.tt_body:
			self.tt_image.blit(absroot.gamedb("font_item_desc").render(self.tt_body, 1, (20,20,20)), (0,absroot.gamedb("font_item_title").size("|")[1]))

		self.tt_image_clip()
		self.tt_add_box()