import types, sys

class AbsrootBase(types.ModuleType):
	version_major=0
	version_minor=3
	version_revision=422
	version="v"+str(version_major)+"."+str(version_minor)+".."+str(version_revision)

_this=AbsrootBase('absroot')

sys.modules['absroot']=_this

#Wow, I really should have done this sooner!