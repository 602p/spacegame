#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pygame
import txtlib

pygame.init()

screen = pygame.display.set_mode((800, 600))

text = txtlib.Text((600, 400), '')

text.html('\n\nProviamo formattazione <U><i><b>html</B></i></U>. <color="255, 0, 0">Colore</color>, <size="10">size</s>, <foNt="azfhh">font</FONT>')

text.update()

screen.blit(text.area, (200, 100))
pygame.display.flip()

while True:
	event = pygame.event.wait()
	if event.type == pygame.QUIT:
		exit(0)