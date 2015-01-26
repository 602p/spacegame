import time
import extention_loader, pygame, ui_states, item
from logging import debug, info, warning, error, critical

SECRET_KEY = pygame.K_F9

class supersecreteasteregg(extention_loader.HookableExtention):
	def __init__(self, root):
		self.root=root
	def event_state(self, state, event):
		if state=="game":
			if event.type==pygame.KEYDOWN:
				if event.key==SECRET_KEY:
					print("Success!")
					time.sleep(1)
					print("Alas, the GUI was broken. To work on later.")

def init_inject(root, console):
	info("Injecting the SecretHook")
	extention_loader.safepost(console, "[sebastianmod:supersecreteasteregg]: Injecting the SecretHook", color=(0,255,255), bold=1)                                                                                           
	root.extentions["x_test_secret"]=supersecreteasteregg(root)