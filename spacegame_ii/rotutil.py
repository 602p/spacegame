import pygame, math

def rot_center(image, rect, angle):
	"""rotate an image while keeping its center"""
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = rot_image.get_rect(center=rect.center)
	return rot_image,rot_rect

def rotate_point(centerPoint,point,angle):
	"""Rotates a point around another centerPoint. Angle is in degrees.
	Rotation is counter-clockwise"""
	angle = math.radians(angle)
	temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
	temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
	temp_point = int(temp_point[0]+centerPoint[0]) , int(temp_point[1]+centerPoint[1])
	return temp_point

class ScrollingWorldManager:
	def __init__(self, screen, offset_x=0, offset_y=0):
		self.screen=screen
		self.offset_x=offset_x
		self.offset_y=offset_y
	def blit(self, image, coords):
		if coords[0]>self.offset_x-3000 and coords[0]<self.offset_x+3000 and coords[1]>self.offset_y-3000 and coords[1]<self.offset_y+3000:
			self.screen.blit(image, (coords[0]-self.offset_x, coords[1]-self.offset_y))
	def set_offset(self, offset):
		self.offset_x=offset[0]
		self.offset_y=offset[1]
	def draw_line(self, color, start, end, thickness=1):
		pygame.draw.line(self.screen, color, (start[0]-self.offset_x, start[1]-self.offset_y),(end[0]-self.offset_x, end[1]-self.offset_y), thickness)
	def draw_rect(self, color, rect, width):
		pygame.draw.rect(self.screen, color, ((rect.x-self.offset_x, rect.y-self.offset_y),rect.size), width)

def aspect_scale(img,(bx,by)):
	""" Scales 'img' to fit into box bx/by.
	 This method will retain the original image's aspect ratio """
	ix,iy = img.get_size()
	if ix > iy:
	    # fit to width
	    scale_factor = bx/float(ix)
	    sy = scale_factor * iy
	    if sy > by:
	        scale_factor = by/float(iy)
	        sx = scale_factor * ix
	        sy = by
	    else:
	        sx = bx
	else:
	    # fit to height
	    scale_factor = by/float(iy)
	    sx = scale_factor * ix
	    if sx > bx:
	        scale_factor = bx/float(ix)
	        sx = bx
	        sy = scale_factor * iy
	    else:
	        sy = by

	return pygame.transform.scale(img, (int(sx),int(sy)))