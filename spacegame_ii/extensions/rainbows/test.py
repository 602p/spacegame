#!/usr/bin/env python

""" GetGlyphs is a function that will run through a given surface and retrieve all 
     shapes of a given color. It packs each shape into a list of coordinate pairs,
     and then packs them all up in a list. It does NOT recognize what shape it has
     found, but with some cleverness you could maybe make it into a cheap-OCR kind 
     of thing. 

     I wrote this so you can pick out the letters in a rendered surface and manipulate
     them independantly. 
     
     For shits and giggles, I make it make all the colors rainbow.  That could probably
     be made into a function, or GetGlyphs() could be extended to do a lot of things, 
     or ideally take a string and do stuff automagically. Whatever.

     Note: This is HORRENDOUSLY UNBELIEVABLY PHENOMENALLY SLOW. I have no idea what 
     I am doing and you are more than welcome to make it faster or rewrite it in one 
     line or delete it on sight for being ugly or whatever. On the bright side, 
     it does not crash anymore.
     
     Intention -- Mike Mulchek -- god@seekrut.com -- 12/04/2001 """
     
     
import pygame, pygame.font, random
from pygame.locals import *

def GetGlyphs(surf, COLOR):
     """ Pull All Glyphs and Shapes of a certain color from a certain surface """
     print "Looking for glyphs and shapes... This could take a few minutes..."
     TempGlyph = []      # Temporary Letter
     GlyphList = []      # Finished Glyph binder
     Active = []         # Scratch space
     
     SurfCopy = pygame.Surface(surf.get_size())   # Make a copy so we do not destroy anything
     SurfCopy.blit(surf, (0,0))

     DONECOLOR = (random.randrange(10,250),random.randrange(10,250),random.randrange(10,250))
     if DONECOLOR == COLOR:
          DONECOLOR[0] += 1        # Pick a scratch color that is guaranteed not to be the one we're looking for

     for x in range(SurfCopy.get_width()):             # Run over the entire surface until we find a pixel to start with
          for y in range(SurfCopy.get_height()):
               if SurfCopy.get_at([x,y])[:3] == COLOR:      # [:3] is to chop off the alpha info.. if true, start pulling the glyph!
                    TempGlyph = []
                    Active = []
                    Active.append([x,y])
                    while len(Active):                      # Check adjacent to a good-pixel in the order [Right Left Down Up]
                         CurrPoint = Active.pop(0)               # Keep adding good-color pixels...
                         Point = [CurrPoint[0],CurrPoint[1]]     # Throwing them into TempGlyph until there are no more to pull
                         
                         try:
                              if SurfCopy.get_at(  [Point[0]+1, Point[1]]  )[:3] == COLOR:
                                   Active.append(  [Point[0]+1, Point[1]]    )
                                   SurfCopy.set_at([Point[0]+1, Point[1]], DONECOLOR)
                         except IndexError:
                              pass                         # Sometimes you test a nonexistant surface index.. 

                         try:                            
                              if SurfCopy.get_at(  [Point[0]-1, Point[1]]  )[:3] == COLOR:
                                   Active.append(  [Point[0]-1, Point[1]]    )
                                   SurfCopy.set_at([Point[0]-1, Point[1]], DONECOLOR)
                         except IndexError:
                              pass                          # but we don't care, so just ignore it....

                         try:                              
                              if SurfCopy.get_at(  [Point[0], Point[1]+1]  )[:3] == COLOR:
                                   Active.append(  [Point[0], Point[1]+1]    )
                                   SurfCopy.set_at([Point[0], Point[1]+1], DONECOLOR)
                         except IndexError:
                              pass
                              
                         try:
                              if SurfCopy.get_at(  [Point[0], Point[1]-1]  )[:3] == COLOR:
                                   Active.append(  [Point[0], Point[1]-1]    )
                                   SurfCopy.set_at([Point[0], Point[1]-1], DONECOLOR)
                         except IndexError:
                              pass

                         TempGlyph.append(Point)                 # When done searching the pixel, store it away
                    GlyphList.append(TempGlyph)                  # When the letter is done, save it in a binder
                    pygame.display.flip()
     print "There are", 
     print len(GlyphList),
     print "glyphs found altogether..."
     return GlyphList                                            # And when the entire surface is scrubbed, give the binder back
     




if __name__ == '__main__':    # Whatever this does...

     pygame.init()            # Start the pygame

     FALSE = 0                
     TRUE = 1

     ANTIALIAS = FALSE        # Antialiasing sucks. 

     WHITE = (255,255,255)    # Lots of pretty colors
     BLACK = (0,0,0)
     RED = (255,0,0)
     GRAY = (128,128,128)
      
     OLDCOLOR = BLACK         # OLDCOLOR is the color you want to search for
     NEWCOLOR = RED           # NEWCOLOR is the color you would like to change the glyph to
     BACKGROUND = WHITE       # BACKGROUND is the background color
     
     FONTSIZE = 50            # How big to make the font?
     
     Messages = []            # A list to keep your messages in
     Surfaces = []            # A list of surfaces the messages will render to
          
     Messages.append("Hello there.")     # What do you want to say?  Add as many as you like.
     Messages.append("How are you?")
     Messages.append("This program is dull...")
     Messages.append("But is pretty when you click?!")

     CurrentFont = pygame.font.Font(None, FONTSIZE)  # Set up a default font

     for x in Messages:       # Generate all of our messages
          Surfaces.append(CurrentFont.render(x, ANTIALIAS, OLDCOLOR, BACKGROUND)) 


     # A bunch of ugly crap to paste all the surfaces to the screen all lined up pretty

     MaxWidth = []
     TotalHeight = 0
     CurrentHeight = 0

     for x in Surfaces:
          MaxWidth.append(x.get_width())

     for x in Surfaces:
          TotalHeight += x.get_height()

     screen = pygame.display.set_mode([max(MaxWidth),TotalHeight] )
     screen.fill(BACKGROUND)     

     for x in Surfaces:
          screen.blit(x, (0,CurrentHeight))
          CurrentHeight += x.get_height()
          
     pygame.display.flip()


     # Finally, we are done with the test surface. Now to pull out the letters.
     
     Glyphs = GetGlyphs(screen, OLDCOLOR)

     # Super seekrut magic colorize

     for G in Glyphs:
          RANDCOLOR = (random.randrange(0,256),random.randrange(0,256),random.randrange(0,256))
          for Point in G:
               screen.set_at(Point, RANDCOLOR)


     while pygame.event.poll().type != QUIT:
          if pygame.mouse.get_pressed()[0]:
               for G in Glyphs:
                    RANDCOLOR = (random.randrange(0,256),random.randrange(0,256),random.randrange(0,256))
                    for Point in G:
                         screen.set_at(Point, RANDCOLOR)
          pygame.display.flip()
          