import types, sys

class AbsrootBase(types.ModuleType):
	pass

_this=AbsrootBase('absroot')

sys.modules['absroot']=_this

#Wow, I really should have done this sooner!