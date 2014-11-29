def f():
	return 100

def seive(n):
	'''\
	Returns a list of all prime numbers less than n
	Parameters: n - int
	'''
	
	primes = [0,0] + [1]*(n-2)
	for i in xrange(2, n):
		if primes[i] == 0:
			continue
		else:
			j = 2*i
			while j < n:
				primes[j] = 0
				j+=i
	return [m for m in xrange(0, n) if primes[m] == 1]


def line(start_pos, end_pos, color=[0,0,0], width=1):
	'''\
	Call pygame.draw.line
	Parameters:
		start_pos - x,y coordinate of start point
		end_pos - x,y coordinate of end point
		color - Line color in RGB format
		width - Line thickness 
	'''
	pygame.draw.line(Draw_Screen, color, start_pos, end_pos, width)

def polygon(pointlist, color=[0,0,0], width=0):
	'''\
	Call pygame.draw.polygon
	Parameters:
		pointlist - list of vertices
		color - Line color in RGB format
		width - Line thickness 
	'''
	pygame.draw.polygon(Draw_Screen, color, pointlist, width)

def circle(pos, radius, color=[0,0,0], width=0):
	'''\
	Call pygame.draw.circle
	Parameters:
		pos - x,y center of circle
		radius - radius of circle
		color - Line color in RGB format
		width - Line thickness 
	'''
	pygame.draw.circle(Draw_Screen, color, pos, radius, width)
