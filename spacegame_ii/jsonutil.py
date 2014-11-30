
def dget(dictx, att, default):
	if att in dictx:
		return dictx[att]
	return default