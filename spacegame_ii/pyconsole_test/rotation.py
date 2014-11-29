import pyconsole
import pygame, sys
from pygame.locals import *
from math import radians, cos, sin, sqrt
from numarray import array, matrixmultiply, transpose

theta1 = 0
theta2 = 0
theta3 = 0

X = 0
Y = 1
Z = 2

draw_pos = [300,200]


class TransformationMatrix:
	def __init__(self, rows, cols):
		self.T = self.identity(dim)
		self.dim = dim
	def identity(self, dim):
		return numarray.identity(dim)
	def transformPoints(self, vector):
		b = matrixmultiply(self.T, vector)
		return b
		
	
def gen_rotations(theta1, theta2, theta3):
	global rot_matrix
	theta1, theta2, theta3 = radians(theta1), radians(theta2), radians(theta3)
	rotate_x  = array(sequence=(1,	0,				0,
								0,	cos(theta1),	-sin(theta1),
								0,	sin(theta1),	cos(theta1)),shape=(3,3))

	rotate_y  = array(sequence=(cos(theta2),0,	-sin(theta2),
								0,			1,	0,
								sin(theta2),0,	cos(theta2)),shape=(3,3))
								
	rotate_z  = array(sequence=(cos(theta3),	-sin(theta3),	0,
								sin(theta3),	cos(theta3),	0,
								0,				0,				1,),shape=(3,3))
	rot_matrix = matrixmultiply(matrixmultiply(rotate_z,rotate_y),rotate_x)

gen_rotations(0,0,0)
# Set initial rotation speeds


def scale_point(point, factor):
	t_scale = array(sequence=(factor,		 0,		0,
								   0,	factor,		0,
								   0,		 0, factor), shape=(3,3))
	return matrixmultiply(t_scale, array(sequence=point, shape=(3,1))).tolist()


def main():
	G_Screen = pygame.display.set_mode((600,480))
	cube_color = [0x0,0xFF,0x0]

	console = pyconsole.Console(G_Screen, (0,0,600,240), vars={"color":cube_color}, functions={"set_rot":gen_rotations}, key_calls={'d':sys.exit})
	
	rps2 = [(100,100,-150),(-100,100,-150),(-100,-100,-150),(100,-100,-150),(0,0,150)]
	rps = [[100,100,-100],[-100,100,-100],[-100,-100,-100],[100,-100,-100],[100,-100,100],[-100,-100,100], [-100,100,100], [100,100,100]]
		
	polygons_c = [	polygon([rps[0]]+[rps[1]]+[rps[2]]+[rps[3]], cube_color), #Back
					polygon([rps[4]]+[rps[5]]+[rps[6]]+[rps[7]], cube_color),#Front
					polygon([rps[0]]+[rps[3]]+[rps[4]]+[rps[7]], cube_color),#Right
					polygon([rps[1]]+[rps[2]]+[rps[5]]+[rps[6]], cube_color),#Left
					polygon([rps[2]]+[rps[3]]+[rps[4]]+[rps[5]], cube_color),#Bottom
					polygon([rps[0]]+[rps[1]]+[rps[6]]+[rps[7]], cube_color)]#Top
	
	polygons_t = [	polygon([rps2[0]]+[rps2[1]]+[rps2[2]]+[rps2[3]]),
					polygon([rps2[0]]+[rps2[1]]+[rps2[4]]),
					polygon([rps2[1]]+[rps2[2]]+[rps2[4]]),
					polygon([rps2[2]]+[rps2[3]]+[rps2[4]]),
					polygon([rps2[3]]+[rps2[0]]+[rps2[4]]),]
	
	
	cube = Shape(polygons_c, [0x0,0xFF,0x0])
	pyramid = Shape(polygons_t, [0x0,0xFF,0xFF])
	
	while 1:
		G_Screen.fill([0xFF,0xFF,0xFF])
		cube_color = console.getvar("color")
		console.process_input()
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_w and pygame.key.get_mods() & KMOD_CTRL:
					console.set_active()
				elif event.key == K_UP:
					for p in range(len(rps)):
						rps[p] = scale_point(rps[p], 1.01)
				elif event.key == K_DOWN:
					for p in range(len(rps)):
						rps[p] = scale_point(rps[p], 0.99)
				elif event.key == K_a:
					draw_pos[X] -= 5
				elif event.key == K_d:
					draw_pos[X] += 5					
				elif event.key == K_w:
					draw_pos[Y] -= 5
				elif event.key == K_s:
					draw_pos[Y] += 5
		#tmplist = []
		#for point in rps:
		#p = matrixmultiply(rot_matrix, array(sequence=rps, shape=(3, len(rps))))
		#tmplist.append(p.tolist())
		#rps = tmplist
		cube.transform(rot_matrix)
		pyramid.transform(rot_matrix)


		cube.draw(G_Screen)
		pyramid.draw(G_Screen)
		console.draw()
		pygame.display.flip()
		pygame.time.wait(10)
		

class polygon:
	def __init__(self, plist, color=[0xFF,0xFF,0xFF]):
		self.points = plist
		self.color = color
	def __cmp__(self, other):
		ls = len(self.points)
		lo = len(other.points)
		avg_self = sum(self.points[i][Z] for i in range(ls))/ls
		avg_other = sum(other.points[i][Z] for i in range(lo))/lo
		return cmp(avg_self, avg_other)
	def draw(self, surface):
		pygame.draw.polygon(surface, self.color, [[int(i[X])+draw_pos[X],int(i[Y])+draw_pos[Y]] for i in self.points])
		pygame.draw.polygon(surface, [0x0,0x0,0x0], [[int(i[X])+draw_pos[X],int(i[Y])+draw_pos[Y]] for i in self.points],2)
	def transform(self, t):
		tmp = transpose(array(sequence=self.points, shape=(len(self.points), 3)))
		self.points = transpose(matrixmultiply(t, tmp)).tolist()

		

class Shape:
	def __init__(self, polygons, color):
		self.polygons = polygons
		self.color = color
	def transform(self, t):
		for poly in self.polygons:
			poly.transform(t)
	def draw(self, surface):
		self.polygons.sort()
		for poly in self.polygons:
			poly.draw(surface)
	

if __name__ == "__main__":
	main()
