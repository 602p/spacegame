from logging import debug
import logging
module_logger=logging.getLogger("sg.formatting")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


class Formatter(object):
	def __init__(self, modules={"t_int":1}):
		self.modules=modules
		self.modules.update({
			"formatter":self
		})

	def format_string(self, full_string):
		for __count in xrange(0,full_string.count("<@{")):
			o_substring=full_string[full_string.find("<@{"):full_string.find("}>")+2]
			substring=o_substring[3:len(o_substring)-2]
			self.modules.update({
				"substring":substring
			})
			#print substring
			
			ref=substring.split(":",1)[0]
			cmd=substring.split(":",1)[1]
			#print ref
			#print cmd

			debug("Processing o_:"+o_substring+" with pc_:"+"self.modules[ref]."+cmd+" to...")

			full_string=full_string.replace(o_substring, str(eval("self.modules[ref]."+cmd)))
			debug("f_s_:"+full_string)
			#print full_string
			#print
		return full_string

class SubFormatter(Formatter):
	def __init__(self, base, add_modules):
		self.modules={}
		self.modules.update(base.modules)
		self.modules.update(add_modules)