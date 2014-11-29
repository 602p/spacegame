import os, pygame

def load_image(package_root, path):
	if path=="$BLANK":
		if pygame.display.get_init():
			return pygame.Surface((0,0))
		else:
			return None
	return pygame.image.load(os.path.join(package_root, path)).convert_alpha()