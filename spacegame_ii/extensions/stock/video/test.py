from __future__ import division
import pygame, time

FPS = 60

pygame.init()
clock = pygame.time.Clock()
movie = pygame.movie.Movie('klingon_dishonor.mpg')
screen = pygame.display.set_mode(movie.get_size())
movie_screen = pygame.Surface(movie.get_size()).convert()

movie.set_display(movie_screen)
movie.play()

time=0.0
playing = True
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            movie.stop()
            playing = False

    screen.blit(movie_screen,(0,0))
    pygame.display.update()
    clock.tick(FPS)
    time+=1.0/(clock.get_fps()+20)
    print time
    if time>9.5:
    	playing=False

pygame.quit()