STATUS = True

from logging import debug, info, warning, error, critical
def init_enableloader(root):
	info("loader_enable::init_enableloader: Turning the loading screen "+"on" if STATUS else "off")
	root.settings["graphics"]["loader_screen"]=STATUS