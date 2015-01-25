
"""
The way I should set this up is as a alternative to the % operator, where I can do stuff like @(citem#->get_center()) from within text and have it get replaced with (19291, 1293).
You can define any number of 'root ids,' for example root, and gamestate.
Then, you can use a SubFormatter to merge local ids like item (in a primitive) with the root nodes availible too.

Examples: In a primitive, you might post a message as:
 @{citem#->parent.get_owner_name()}'s @{citem#::parent.name} shot a @{citem#::name}

and it would format to:
 John Smith's Raider shot a Basic Laser

using code like:
 root.formatter.format(unformatted_string, Formatter({"citem":item}))

meaning you are using the root formatter supplemented by a formatter defining citem as the primitive call's item attribute

citem->parent.formatter('')
"""

class Formatter(object):
	def __init__(self, modules={}):
		self.modules=modules

	def __str__(self):
		return "no"

	def format_string(self, full_string, modules={}):
		temp_dict={}
		temp_dict.update(self.modules)
		temp_dict.update(modules)
		for __count in xrange(0,full_string.count("<@{")):
			substring=full_string[full_string.find("<@{"):full_string.find("}>")+2]
			full_string=full_string.replace(substring, self.format_insert(substring, temp_dict), 1)
		return full_string

	def format_insert(self, string, modules):
		parsed_string_=string.strip().replace("<@{","",1)
		parsed_string=""
		for i in reversed(parsed_string_): parsed_string+=i
		parsed_string=parsed_string.strip()
		parsed_string=parsed_string.replace(">}","",1)
		parsed_string_f=""
		for i in reversed(parsed_string): parsed_string_f+=i
		parsed_string_f=parsed_string_f.strip()
		
		module=modules[parsed_string_f.split("::")[0]]
		string=parsed_string_f.split("::",1)[1]
		___formatter___=self
		___modules___=modules
		___module___=module
		___string___=string
		#Clean out namespace by removing refs
		del self
		del modules
		del module
		del parsed_string_
		del parsed_string
		del parsed_string_f
		del string
		return str(eval('___module___.'+___string___))

class SubFormatter(Formatter):
	def __init__(self, parent, additions):
		self.modules={}
		self.modules.update(parent.modules)
		self.modules.update(additions)