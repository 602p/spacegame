import jsonpatch, extention_loader, absroot, logging
module_logger=logging.getLogger("x.modulemanager")
debug, info, warning, error, critical = module_logger.debug, module_logger.info, module_logger.warning, module_logger.error, module_logger.critical


def load_mm_patch(json_data, basepath, dirn, filen, console):
	json_data["name"]="mmpatchkey_"+str(id(json_data))+"_"+str(len(str(json_data)))+"_"+dirn+"/"+filen+"_"+basepath
	absroot.json_patches.append(json_data)

def apply_mm_patch(json_data, basepath, dirn, filen, console):
	c=0
	for asset in absroot.json_patches:
		patch=jsonpatch.JsonPatch(asset["patch"])
		try:
			patch.apply(json_data, True)
			debug("Applied "+asset["name"]+" ...")
			c+=1
		except jsonpatch.JsonPatchTestFailed:
			pass
	if c>0:
		extention_loader.safepost(absroot.loader_renderer, "    (Applied "+str(c)+" JsonPatch operations)", italic=1)

@extention_loader.hook_extention("mm_install")
class MMHook(extention_loader.HookableExtention):
	name="ModuleManager"
	desc="Allows JSONPatch operations at runtime"

	def after_plugins_load(self):
		absroot.json_patches=[]
		for ext in absroot.gamedb.extention_loaders:
			absroot.gamedb.extention_loaders[ext].insert(0, apply_mm_patch)

		absroot.gamedb.json_extentions.insert(0, ".jpatch")
		absroot.gamedb.extention_loaders[".jpatch"]=[load_mm_patch]
		debug("after_plugins_load complete: Listing extention_loaders:")
		for ext in absroot.gamedb.extention_loaders:
			debug("\t"+ext+"\t--> "+str(absroot.gamedb.extention_loaders[ext]))