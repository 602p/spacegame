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
	def __init__(self, root, screen, offset_x=0, offset_y=0):
		self.screen=screen
		self.root=root
		self.offset_x=offset_x
		self.offset_y=offset_y
	def get_t_coords(self, pos):
		return (pos[0]-self.offset_x, pos[1]-self.offset_y)
	def get_t_rect(self, rect):
		rect=rect.copy()
		rect.topleft=self.get_t_coords(rect)
		return rect
	def blit(self, image, coords):
		if self.root.settings["debug"]["overrender"]:self.draw_rect((0,0,255), pygame.Rect(coords, image.get_size()))
		if (coords[0]-self.offset_x<self.screen.get_size()[0] and coords[1]-self.offset_y<self.screen.get_size()[1]) and (coords[0]-self.offset_x > -800 and coords[1]-self.offset_y>-800):
			self.screen.blit(image, (coords[0]-self.offset_x, coords[1]-self.offset_y))
	def set_offset(self, offset):
		self.offset_x=offset[0]
		self.offset_y=offset[1]
	def draw_line(self, color, start, end, thickness=1):
		pygame.draw.line(self.screen, color, (start[0]-self.offset_x, start[1]-self.offset_y),(end[0]-self.offset_x, end[1]-self.offset_y), thickness)
	def draw_rect(self, color, rect, width=0):
		pygame.draw.rect(self.screen, color, ((rect.x-self.offset_x, rect.y-self.offset_y),rect.size), width)
	def clamp(self, rect):
		rect2=rect.copy()
		rect2.x-=self.offset_x
		rect2.y-=self.offset_y
		rect2.clamp_ip(self.screen.get_rect())
		return rect2
	def blit_clamped(self, image, rect):
		rect2=self.clamp(rect)
		self.screen.blit(image, rect2)

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

def get_angle(x1, x2, y1, y2):
	delta_angle=math.degrees(math.atan2(y2-y1, -(x2-x1)))+90
	return delta_angle

def get_rel_angle(delta_angle, self_angle):
	return math.degrees(math.atan2(
			math.sin(math.radians(delta_angle)-math.radians(self_angle)),
			math.cos(math.radians(delta_angle)-math.radians(self_angle))
		))