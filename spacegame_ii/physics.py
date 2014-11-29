from __future__ import division
 
################## http://www.pygame.org/wiki/2DVectorClass ##################
import operator
import math
 
class Vec2d(object):
	"""2d vector class, supports vector and scalar operators,
	   and also provides a bunch of high level functions
	   """
	__slots__ = ['x', 'y']
 
	def __init__(self, x_or_pair, y = None):
		if y == None:
			self.x = x_or_pair[0]
			self.y = x_or_pair[1]
		else:
			self.x = x_or_pair
			self.y = y
 
	def __len__(self):
		return 2
 
	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		else:
			raise IndexError("Invalid subscript "+str(key)+" to Vec2d")
 
	def __setitem__(self, key, value):
		if key == 0:
			self.x = value
		elif key == 1:
			self.y = value
		else:
			raise IndexError("Invalid subscript "+str(key)+" to Vec2d")
 
	# String representaion (for debugging)
	def __repr__(self):
		return 'Vec2d(%s, %s)' % (self.x, self.y)
 
	# Comparison
	def __eq__(self, other):
		if hasattr(other, "__getitem__") and len(other) == 2:
			return self.x == other[0] and self.y == other[1]
		else:
			return False
 
	def __ne__(self, other):
		if hasattr(other, "__getitem__") and len(other) == 2:
			return self.x != other[0] or self.y != other[1]
		else:
			return True
 
	def __nonzero__(self):
		return bool(self.x or self.y)
 
	# Generic operator handlers
	def _o2(self, other, f):
		"Any two-operator operation where the left operand is a Vec2d"
		if isinstance(other, Vec2d):
			return Vec2d(f(self.x, other.x),
						 f(self.y, other.y))
		elif (hasattr(other, "__getitem__")):
			return Vec2d(f(self.x, other[0]),
						 f(self.y, other[1]))
		else:
			return Vec2d(f(self.x, other),
						 f(self.y, other))
 
	def _r_o2(self, other, f):
		"Any two-operator operation where the right operand is a Vec2d"
		if (hasattr(other, "__getitem__")):
			return Vec2d(f(other[0], self.x),
						 f(other[1], self.y))
		else:
			return Vec2d(f(other, self.x),
						 f(other, self.y))
 
	def _io(self, other, f):
		"inplace operator"
		if (hasattr(other, "__getitem__")):
			self.x = f(self.x, other[0])
			self.y = f(self.y, other[1])
		else:
			self.x = f(self.x, other)
			self.y = f(self.y, other)
		return self
 
	# Addition
	def __add__(self, other):
		if isinstance(other, Vec2d):
			return Vec2d(self.x + other.x, self.y + other.y)
		elif hasattr(other, "__getitem__"):
			return Vec2d(self.x + other[0], self.y + other[1])
		else:
			return Vec2d(self.x + other, self.y + other)
	__radd__ = __add__
 
	def __iadd__(self, other):
		if isinstance(other, Vec2d):
			self.x += other.x
			self.y += other.y
		elif hasattr(other, "__getitem__"):
			self.x += other[0]
			self.y += other[1]
		else:
			self.x += other
			self.y += other
		return self
 
	# Subtraction
	def __sub__(self, other):
		if isinstance(other, Vec2d):
			return Vec2d(self.x - other.x, self.y - other.y)
		elif (hasattr(other, "__getitem__")):
			return Vec2d(self.x - other[0], self.y - other[1])
		else:
			return Vec2d(self.x - other, self.y - other)
	def __rsub__(self, other):
		if isinstance(other, Vec2d):
			return Vec2d(other.x - self.x, other.y - self.y)
		if (hasattr(other, "__getitem__")):
			return Vec2d(other[0] - self.x, other[1] - self.y)
		else:
			return Vec2d(other - self.x, other - self.y)
	def __isub__(self, other):
		if isinstance(other, Vec2d):
			self.x -= other.x
			self.y -= other.y
		elif (hasattr(other, "__getitem__")):
			self.x -= other[0]
			self.y -= other[1]
		else:
			self.x -= other
			self.y -= other
		return self
 
	# Multiplication
	def __mul__(self, other):
		if isinstance(other, Vec2d):
			return Vec2d(self.x*other.x, self.y*other.y)
		if (hasattr(other, "__getitem__")):
			return Vec2d(self.x*other[0], self.y*other[1])
		else:
			return Vec2d(self.x*other, self.y*other)
	__rmul__ = __mul__
 
	def __imul__(self, other):
		if isinstance(other, Vec2d):
			self.x *= other.x
			self.y *= other.y
		elif (hasattr(other, "__getitem__")):
			self.x *= other[0]
			self.y *= other[1]
		else:
			self.x *= other
			self.y *= other
		return self
 
	# Division
	def __div__(self, other):
		return self._o2(other, operator.div)
	def __rdiv__(self, other):
		return self._r_o2(other, operator.div)
	def __idiv__(self, other):
		return self._io(other, operator.div)
 
	def __floordiv__(self, other):
		return self._o2(other, operator.floordiv)
	def __rfloordiv__(self, other):
		return self._r_o2(other, operator.floordiv)
	def __ifloordiv__(self, other):
		return self._io(other, operator.floordiv)
 
	def __truediv__(self, other):
		return self._o2(other, operator.truediv)
	def __rtruediv__(self, other):
		return self._r_o2(other, operator.truediv)
	def __itruediv__(self, other):
		return self._io(other, operator.floordiv)
 
	# Modulo
	def __mod__(self, other):
		return self._o2(other, operator.mod)
	def __rmod__(self, other):
		return self._r_o2(other, operator.mod)
 
	def __divmod__(self, other):
		return self._o2(other, operator.divmod)
	def __rdivmod__(self, other):
		return self._r_o2(other, operator.divmod)
 
	# Exponentation
	def __pow__(self, other):
		return self._o2(other, operator.pow)
	def __rpow__(self, other):
		return self._r_o2(other, operator.pow)
 
	# Bitwise operators
	def __lshift__(self, other):
		return self._o2(other, operator.lshift)
	def __rlshift__(self, other):
		return self._r_o2(other, operator.lshift)
 
	def __rshift__(self, other):
		return self._o2(other, operator.rshift)
	def __rrshift__(self, other):
		return self._r_o2(other, operator.rshift)
 
	def __and__(self, other):
		return self._o2(other, operator.and_)
	__rand__ = __and__
 
	def __or__(self, other):
		return self._o2(other, operator.or_)
	__ror__ = __or__
 
	def __xor__(self, other):
		return self._o2(other, operator.xor)
	__rxor__ = __xor__
 
	# Unary operations
	def __neg__(self):
		return Vec2d(operator.neg(self.x), operator.neg(self.y))
 
	def __pos__(self):
		return Vec2d(operator.pos(self.x), operator.pos(self.y))
 
	def __abs__(self):
		return Vec2d(abs(self.x), abs(self.y))
 
	def __invert__(self):
		return Vec2d(-self.x, -self.y)
 
	# vectory functions
	def get_length_sqrd(self):
		return self.x**2 + self.y**2
 
	def get_length(self):
		return math.sqrt(self.x**2 + self.y**2)
	def __setlength(self, value):
		length = self.get_length()
		self.x *= value/length
		self.y *= value/length
	length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")
 
	def rotate(self, angle_degrees):
		radians = math.radians(angle_degrees)
		cos = math.cos(radians)
		sin = math.sin(radians)
		x = self.x*cos - self.y*sin
		y = self.x*sin + self.y*cos
		self.x = x
		self.y = y
 
	def rotated(self, angle_degrees):
		radians = math.radians(angle_degrees)
		cos = math.cos(radians)
		sin = math.sin(radians)
		x = self.x*cos - self.y*sin
		y = self.x*sin + self.y*cos
		return Vec2d(x, y)
 
	def get_angle(self):
		if (self.get_length_sqrd() == 0):
			return 0
		return math.degrees(math.atan2(self.y, self.x))
	def __setangle(self, angle_degrees):
		self.x = self.length
		self.y = 0
		self.rotate(angle_degrees)
	angle = property(get_angle, __setangle, None, "gets or sets the angle of a vector")
 
	def get_angle_between(self, other):
		cross = self.x*other[1] - self.y*other[0]
		dot = self.x*other[0] + self.y*other[1]
		return math.degrees(math.atan2(cross, dot))
 
	def normalized(self):
		length = self.length
		if length != 0:
			return self/length
		return Vec2d(self)
 
	def normalize_return_length(self):
		length = self.length
		if length != 0:
			self.x /= length
			self.y /= length
		return length
 
	def perpendicular(self):
		return Vec2d(-self.y, self.x)
 
	def perpendicular_normal(self):
		length = self.length
		if length != 0:
			return Vec2d(-self.y/length, self.x/length)
		return Vec2d(self)
 
	def dot(self, other):
		return float(self.x*other[0] + self.y*other[1])
 
	def get_distance(self, other):
		return math.sqrt((self.x - other[0])**2 + (self.y - other[1])**2)
 
	def get_dist_sqrd(self, other):
		return (self.x - other[0])**2 + (self.y - other[1])**2
 
	def projection(self, other):
		other_length_sqrd = other[0]*other[0] + other[1]*other[1]
		projected_length_times_other_length = self.dot(other)
		return other*(projected_length_times_other_length/other_length_sqrd)
 
	def cross(self, other):
		return self.x*other[1] - self.y*other[0]
 
	def interpolate_to(self, other, range):
		return Vec2d(self.x + (other[0] - self.x)*range, self.y + (other[1] - self.y)*range)
 
	def convert_to_basis(self, x_vector, y_vector):
		return Vec2d(self.dot(x_vector)/x_vector.get_length_sqrd(), self.dot(y_vector)/y_vector.get_length_sqrd())
 
	def __getstate__(self):
		return [self.x, self.y]
 
	def __setstate__(self, dict):
		self.x, self.y = dict

class Vector2d:
	"""Good vector class"""
	def __init__(self, magnitude=0, angle=0):
		self.magnitude=magnitude
		self.angle=angle
	def x(self):
		return math.sin(math.radians(self.angle)) * self.magnitude
	def y(self):
		return math.cos(math.radians(self.angle)) * self.magnitude
	def add_x(self, x):
		self.add_xy(x, 0)
	def add_y(self, y):
		self.add_xy(0,y)
	def add_xy(self, x, y):
		self.angle=math.degrees(math.atan2(self.y, self.x))
		self.magnitude=math.sqrt(self.x**2 + self.y**2)
	def add_raw(self, v):
		self.magnitude+=v

class RigidBody2D:
	def __init__(self, mass=1, x=0, y=0, vector=None):
		if not vector:
			vector=Vector2d(0,0)
		assert isinstance(vector, Vector2d)
		self.x=float(x)
		self.y=float(y)
		self._vector=vector
		self.mass=mass
		self.last_time_constant=0.01

	def get_accel(self, force):
		return (force/self.mass)*self.last_time_constant

	def get_force(self, accel):
		return accel*self.mass

	def get_x_vel(self):
		return self._vector.x()

	def get_y_vel(self):
		return self._vector.y()

	def moving(self):
		return (abs(self.get_x_vel())+abs(self.get_y_vel()))>1

	def get_magnitude(self):
		return self._vector.magnitude

	def set_magnitude(self, m):
		self._vector.magnitude=m

	def exert_in_vector(self, force):
		self._vector.add_raw(self.get_accel(force))

	def exert_in_x(self, force):
		self._vector.add_x(self.get_accel(force))

	def exert_in_y(self, accel):
		self._vector.add_y(self.get_accel(force))

	def rotate(self, angle):
		self._vector.angle+=angle*self.last_time_constant
		if self._vector.angle>360:
			self.set_angle(self._vector.angle-360)
		elif self._vector.angle<0:
			self.set_angle(360-abs(self._vector.angle))

	def set_angle(self, angle):
		self._vector.angle=angle

	def get_angle(self):
		return self._vector.angle

	def update_in_seconds(self, time):
		self.x-=self._vector.x()*time
		self.y-=self._vector.y()*time
		self.last_time_constant=time