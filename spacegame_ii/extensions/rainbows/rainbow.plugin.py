import extention_loader, pygame, ui_states, item
import logging, random, string
module_logger=logging.getLogger("plugin.ranbows")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

COUNT=30

class Rainbow(extention_loader.HookableExtention):
	def tick(self, state):
		self.color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))

	def get_color(self):
		return self.color

	def get_bold(self):
		return random.choice([1,0,0])

	def get_italic(self):
		return random.choice([1,0,0])

	def get_desc(self):
		return "".join(random.sample(string.printable, 100))

def init_inject(root, console):
	info("Adding el rainbow")
	extention_loader.safepost(console, "Adding el rainbow", color=(170, 0, 170), bold=1)
	for c in xrange(COUNT):
		root.extentions["rainbow"+hex(c)]=Rainbow(root)