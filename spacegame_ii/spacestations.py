import state, albow

class MenuScreen(Screen):

	def __init__(self, shell):
		Screen.__init__(self, shell)
		self.shell = shell
		title = Label("Albow Demo", font = shell.root.gamedb("font_standard_small"))
		menu = Column([
			Button("Quit", shell.quit),
		], align = 'l')
		contents = Column([
			title,
			menu,
		], align = 'l', spacing = 20)
		self.add_centered(contents)
	
	def quit(self):
		sys.exit(0)

class SpaceStationShell(Shell):
	def __init__(self, display, root):
		self.root=root
		Shell.__init__(self, display)
		self.create_screens()
		self.menu_screen = MenuScreen(self) # Do this last
		self.set_timer(frame_time)
		self.show_menu()
	
	def create_screens(self):
		pass

	def show_menu(self):
		self.show_screen(self.menu_screen)
	
	def begin_frame(self):
		self.anim_screen.begin_frame()

class SpaceStationState(state.State):
	def first_start(self):
		self.shell=SpaceStationShell(self.root.screen.screen)