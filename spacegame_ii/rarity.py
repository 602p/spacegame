from __future__ import division
import random, absroot

MIN    =   60
HR     =   3600
DAY    =   86400
WK     =   604800

class Rarity:
	def __init__(self, json):
		self.default=json.get("default",-1)
		self.factions=json.get("factions",[])

	def __get_for(self, faction_key):
		for i in self.factions:
			if i["faction"]==faction_key:
				return i["rarity"]
		return self.default

	def _get_for(self, faction_key):

		rarity = str(self.__get_for(faction_key))
		if "/" in rarity:
			val = eval(rarity.upper()) * 100
		else:
			val = eval(rarity.upper())
		
		return val

	def get_for(self, faction_key):
		if type(faction_key) == list:
			return sum([self._get_for(i) for i in faction_key])+self._get_for("__DOES_NOT_EXIST__")
		else:
			return self.get_for([faction_key])+self._get_for("__DOES_NOT_EXIST__")

	def should_have(self, faction_key, mod=1):
		if random.randint(0,99) < self.get_for(faction_key)*mod:
			return True
		return False

	def should_happen(self, faction_key, dt):
		modified_value=self.get_for(faction_key)*dt*100
		rand_value=random.uniform(0,100)*100
		#print rand_value, " < ", modified_value, "? >> ", rand_value<modified_value
		return  rand_value<modified_value

	def __str__(self, *args, **kwargs):
		r="DEFAULT[]: "+str(self.default)
		for i in self.factions:
			r+="\n-FACTION["+str(i["faction"])+"]:"+str(i["rarity"])
		return r