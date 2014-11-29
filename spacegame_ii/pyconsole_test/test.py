#!/usr/bin/python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Test for pyconsole.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import pyconsole
import pygame, os, sys, re
from pygame.locals import *
from test_syntax import *
from test_functions import *

path = os.path.abspath(os.path.dirname(__file__))
img_path = os.path.join(path, "images")


Background = pygame.Surface((600,480))
bg_img = pygame.image.load(os.path.join(img_path,"testimg.jpg"))
Background.blit(bg_img,(0,0))

bg_color = [0x0,0x0,0x0]

def main():
	G_Screen = pygame.display.set_mode((600,480))
	cheat = False
	
	# An example Console object
	console = pyconsole.Console(
								G_Screen, #The surface you want the console to draw on
								(0,0,600,150), #A rectangle defining the size and position of the console
								functions={"f":f,"prime":seive, "type":type, "line":line, "polygon":polygon, "circle":circle}, # Functions for the console
								key_calls={"d":sys.exit}, # Defines what function Control+char will call, in this case ctrl+d calls sys.exit()
								syntax={re_add:console_add, re_function:console_func}
								)
	pygame.mouse.set_pos(300,240)
	vs = {"cheat":cheat,"a":100, "b":200, "c":300}
	console.setvars(vs)
	while 1:
		G_Screen.fill(bg_color)
		console.process_input()
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_w and pygame.key.get_mods() & KMOD_CTRL:
					console.set_active()
				elif event.key == K_q and pygame.key.get_mods() & KMOD_CTRL: 
					# Just a little hack so you can play with both pyconsole and python
					# Hit ctrl w to hide pyconsole, then ctrl q to switch modes, then ctrl w again to show the console
					# I don't expect anyone to actually use both modes in one app, if you really need to, you can be more creative than this.
					console.setvar("python_mode", not console.getvar("python_mode"))
					console.set_interpreter()
		
		G_Screen.blit(Background,(0,0))
		console.draw()
		pygame.display.flip()
		pygame.time.wait(10)
	

if __name__ == '__main__':
	main()
