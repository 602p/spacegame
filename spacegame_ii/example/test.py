#!/usr/bin/env python

# Copyright (C) 2010-2013  Sam Bull

"""
An example file demonstrating proper use of widgets.

"""

import os
import sys
import random

import pygame
from pygame.locals import *
try:
    from OpenGL.GL import *
except: pass

pygame.display.init()
pygame.font.init()

sys.path.insert(0, "..")

# Change directory if not running from example
p = os.path.split(sys.argv[0])[0]
if p:
    os.chdir(p)

import sgc
from sgc.locals import *

from sgc.__init__ import __version__ as ver_no

screen = sgc.surface.Screen((640,480))#, flags=OPENGL|DOUBLEBUF
clock = pygame.time.Clock()
pygame.scrap.init()

def clear():
    """Clear input box when enter key is pressed."""
    input_box.text = ""


class MainMenu(sgc.Menu):
    """Create a subclass for custom functions."""

    func_dict = lambda self: {"print_input": self.print_input,
                              "remove": self.remove}

    def print_input(self):
        print self["input"].text

sgc.Font.col = (150,150,150)  # TODO Button font colour


# Title
title = sgc.Label(text="Simple Game Code " + ver_no,
                  font=sgc.Font["title"], col=sgc.Font.col)
title.rect.center = (screen.rect.centerx, 40)
title.add()

# Create input_box
input_box = sgc.InputBox(label="Input Box", default="default text...")
input_box.config(pos=(30,120))
input_box.add(order=0)
# Change colour button, on_click event caught in event loop
button = sgc.Button(label="Change\ncolour", pos=(40,200))
# Create FPS counter
fps = sgc.FPSCounter(clock=clock)
fps.rect.midbottom = (screen.rect.w/2, screen.rect.h)
fps.add()
# Pass config file as argument, to have Menu parse file
with open("menu") as menu_file:
    menu = MainMenu(menu=menu_file)

# Display menu on button click, on_click replaced through assignment
btn_menu = sgc.Button(label="Menu", pos=(250,200))
btn_menu.on_click = menu.add


# Input_box for dialog window
password_box = sgc.InputBox(label="Password", default="Enter password...")
password_box.pos = (0,10)
# Button for dialog window
def print_pass():
    print password_box.text
    dialogs[-1].remove()
btn_ok = sgc.Button(label="OK", pos=(30,60))
btn_ok.on_click = print_pass
# Place widgets into a container
dialog_container = sgc.Container(widgets=(password_box, btn_ok), border=10)
# Display dialog window, on_click replaced through inheritance
dialogs = []
class BtnDialog(sgc.Button):
    def on_click(self):
        dialogs.append(sgc.Dialog(widget=dialog_container,
                       title="Window title here..."))
        dialogs[-1].rect.center = screen.rect.center
        dialogs[-1].add()
btn_dialog = BtnDialog(label="Dialog", pos=(460,200))

box_btn = sgc.HBox(widgets=[button, btn_menu, btn_dialog], spacing=70)

scroll_box = sgc.ScrollBox((300, box_btn.rect.h), widget=box_btn)
scroll_box.rect.center = screen.rect.center
scroll_box.add(order=1)

# Radio Buttons
radio1 = sgc.Radio(group="group1", label="Option 1", active=True)
radio2 = sgc.Radio(group="group1", label="Option 2")
radio3 = sgc.Radio(group="group1", label="Option 3")
radio_box = sgc.VBox(widgets=(radio1, radio2, radio3), pos=(40,320))
radio_box.add(order=2)

# Toggle Button
switch = sgc.Switch(label="Switch", pos=(200,320))
switch.add(order=3)

# Scale widget
scale = sgc.Scale(pos=(50,400), show_value=4)
scale.add(order=4)

# Combo box
combo = sgc.Combo(pos=(400,400), values=("Option 1", "Option 2", "Another"))
combo.add(order=5)

# Selectable Label
label = sgc.Label(text="This is a selectable label", selectable=True)
label.rect.midtop = title.rect.midbottom
label.add()

while True:
    time = clock.tick()
    for event in pygame.event.get():
        # Send event to widgets
        sgc.event(event)
        if event.type == GUI:
            if event.widget_type is sgc.Button:
                print "Button event"
            if event.widget is button and event.gui_type == "click":
                button.config(col=[random.randrange(1,200) for x in range(3)])
            elif event.widget is input_box:
                clear()
        elif event.type == KEYDOWN:
            if event.key == K_f:
                fps.toggle()
        elif event.type == QUIT:
            exit()

    # Cleanup removed windows
    for widget in dialogs:
        if not widget.active():
            dialogs.remove(widget)

    if not screen._opengl:
        screen.fill(Color("blue"))
    else:
        glClearColor(0,0,1,1)
        glClear(GL_COLOR_BUFFER_BIT)
    # Update the widgets once for each frame
    sgc.update(time)

    pygame.display.flip()
