import pygame, sggui

pygame.init()

screen=pygame.display.set_mode((500,500))

manager=sggui.GUIManager(screen, None)
manager.add_widget(sggui.OKBox())

while not pygame.QUIT in [e.type for e in pygame.event.get()]:
	manager.do()
	pygame.display.update()