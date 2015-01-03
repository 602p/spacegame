import state, albow
from albow.widget import Widget
from albow.controls import Label, Button, Image, AttrRef, \
	RadioButton, ValueDisplay
from albow.layout import Row, Column, Grid
from albow.fields import TextField, FloatField
from albow.shell import Shell
from albow.screen import Screen
from albow.text_screen import TextScreen
from albow.resource import get_font, get_image
from albow.grid_view import GridView
from albow.palette_view import PaletteView
from albow.image_array import get_image_array
from albow.dialogs import alert, ask
from albow.file_dialogs import \
	request_old_filename, request_new_filename, look_for_file_or_directory
from albow.tab_panel import TabPanel
from albow.table_view import TableView, TableColumn
from logging import debug, info, warning, error, critical

from albow.theme import root, Theme

class MenuScreen(Screen):

	def __init__(self, shell):
		Screen.__init__(self, shell)
		self.shell = shell
		title = Label(shell.config["name"], font = shell.root.gamedb(shell.config["font"]))
		menu = Column([
			Button("Quit", shell.quit)
		], align = 'l')
		contents = Column([
			title,
			menu,
		], align = 'l', spacing = 20)
		self.add_centered(contents)

class SpaceStationShell(Shell):
	def __init__(self, spacestation_config, display, root):
		self.root=root
		self.config=spacestation_config
		Shell.__init__(self, display)
		self.create_screens()
		self.menu_screen = MenuScreen(self) # Do this last
		self.show_menu()
	
	def create_screens(self):
		pass

	def show_menu(self):
		self.show_screen(self.menu_screen)

	def quit(self):
		sys.exit(0)


class SpaceStationState(state.InterdictingState):
	def run_once(self, params):
		debug("SpaceStationState Interacted!")
		root.bg_image=self.root.gamedb(params["bg_image"])
		root.fg_color=(255,255,255)
		debug("config set")
		self.shell=SpaceStationShell(params, self.root.screen.screen, self.root)
		self.shell.run()
		