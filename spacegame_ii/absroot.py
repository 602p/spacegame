import types, sys

IS_IN_DEVENVIRON=True

class AbsrootBase(types.ModuleType):
	version_major=0
	version_minor=5
	version_revision="?"
	
_this=AbsrootBase('absroot')

try:
	with open("buildcount.txt", 'r') as fp:
		_this.version_revision=eval(fp.read())

	if IS_IN_DEVENVIRON:
		_this.version_revision+=1

		with open("buildcount.txt", 'w') as fp:
			fp.write(str(_this.version_revision))
except BaseException as e:
	print "Error in RWOps while getting buildcount"
	print e

_this.version="v"+str(_this.version_major)+"."+str(_this.version_minor)+":"+str(_this.version_revision)

sys.modules['absroot']=_this

#Wow, I really should have done this sooner!