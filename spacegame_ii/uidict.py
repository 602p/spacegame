
class UIDict(dict):
	def getd_recursive(self, node, string):
		splits=string.split(":")

		assert len(splits)>0

		if splits[0].startswith("~"):
			splits[0]=eval(splits[0].replace("~","",1))

		if len(splits)==1: #we're at the end, return the value
			return node[splits[0]]
		else: #we're not, return the next layer of dict
			rebuilt_string=""
			for index in splits[1:]:
				rebuilt_string+=index+":"
			rebuilt_string=rebuilt_string[:-1]
			return self.getd_recursive(node[splits[0]], rebuilt_string)

	def getd(self, string):
		return self.getd_recursive(self, string)

	def g(self, string):
		return self.getd(string)

	def setd_recursive(self, node, string, value, create=True, recursive_create=True):
		splits=string.split(":")

		assert len(splits)>0

		if splits[0].startswith("~"):
			splits[0]=eval(splits[0].replace("~","",1))

		if len(splits)==1: #we're at the end, set the value
			node[splits[0]]=value
		else: #we're not, call setd on the next layer of dict, creating it if it's not there
			if not splits[0] in node.keys():
				if create:
					node[splits[0]]={}
					if not recursive_create:
						create=False
				else:
					raise AttributeError("Node "+splits[0]+" not found, and not allowed to create")

			rebuilt_string=""
			for index in splits[1:]:
				rebuilt_string+=index+":"
			rebuilt_string=rebuilt_string[:-1]
			return self.setd_recursive(node[splits[0]], rebuilt_string, value, create, recursive_create)

	def setd(self, string, value, recursive_create = True, create = True):
		return self.setd_recursive(self, string, value, create=create, recursive_create=recursive_create)

	def s(self, string, value, recursive_create = True, create = True):
		return self.setd(string, value, create=create, recursive_create=recursive_create)

	def deld_recursive(self, node, string):
		splits=string.split(":")

		assert len(splits)>0

		if splits[0].startswith("~"):
			splits[0]=eval(splits[0].replace("~","",1))

		if len(splits)==1: #we're at the end, set the value
			del node[splits[0]]
		else: #we're not, call setd on the next layer of dict, creating it if it's not there
			if not splits[0] in node.keys():
				raise AttributeError("Node "+splits[0]+" not found, can't delete!")

			rebuilt_string=""
			for index in splits[1:]:
				rebuilt_string+=index+":"
			rebuilt_string=rebuilt_string[:-1]
			self.deld_recursive(node[splits[0]], rebuilt_string)

	def deld(self, string):
		self.deld_recursive(self, string)

	def d(self, string):
		self.deld(string)

	def __setitem__(self, name, value):
		if ":" in name:
			self.setd(name, value)
		else:
			dict.__setitem__(self, name, value)

	def __getitem__(self, name):
		if ":" in name:
			return self.getd(name)
		else:
			return dict.__getitem__(self, name)

	def __delitem__(self, name):
		if ":" in name:
			self.deld(name)
		else:
			dict.__delitem__(self, name)

class HierarchicalDict(dict):
	aro=[None] #None represents this dict

	def __getitem__(self, name):
		for d in self.aro:
			d_resolved = self if d is None else d
			if name in d_resolved:
				return d_resolved[name]

	def __delitem__(self, name):
		for d in self.aro:
			d_resolved = self if d is None else d
			if name in d_resolved:
				del d_resolved[name]