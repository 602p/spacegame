from __future__ import division
 
################## http://www.pygame.org/wiki/2DVectorClass ##################
import operator
import math
import logging
module_logger=logging.getLogger("sg.physics")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical

 
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
	def save_to_config_node(self):
		return {
			"magnitude":self.magnitude,
			"angle":self.angle
		}

def _load_vector(node):
	return Vector2d(node["magnitude"], node["angle"])

class RigidBody2D:
	def __init__(self, mass=1, x=0, y=0, vector=None):
		if not vector:
			vector=Vector2d(0,0)
		assert isinstance(vector, Vector2d)
		self.x=float(x)
		# print y
		# print type(y)
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
		return self.get_magnitude()

	def get_magnitude(self):
		return self._vector.magnitude

	def set_magnitude(self, m):
		self._vector.magnitude=m

	def exert_in_vector(self, force, cap=999999):
		self._vector.add_raw(self.get_accel(force))
		if self._vector.magnitude>cap:
			self._vector.magnitude=cap

	def exert_in_x(self, force):
		self._vector.add_x(self.get_accel(force))

	def exert_in_y(self, accel):
		self._vector.add_y(self.get_accel(force))

	def rotate(self, angle):
		self._vector.angle+=angle*self.last_time_constant
		if self._vector.angle>360:
			self.set_angle(self._vector.angle-360)
		elif self._vector.angle<0:
			self.set_angle(360+self._vector.angle)

	def set_angle(self, angle):
		self._vector.angle=angle

	def get_angle(self):
		return self._vector.angle

	def update_in_seconds(self, time):
		self.x-=self._vector.x()*time
		self.y-=self._vector.y()*time
		self.last_time_constant=time

	def save_to_config_node(self):
		return {
			"x":self.x,
			"y":self.y,
			"last_tc":self.last_time_constant,
			"mass":self.mass,
			"vector":self._vector.save_to_config_node()
		}

def _load_rigidbody(config, parent=None):
	vector = _load_vector(config["vector"]) if "vector" in config.keys() else None
	return RigidBody2D(config.get("mass", parent.mass), config["x"], config["y"], vector)