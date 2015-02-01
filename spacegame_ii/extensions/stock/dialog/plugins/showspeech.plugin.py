import primitives
from logging import debug

class ShowSpeech(primitives.BasePrimitive):
	def run_in_dialog(self, dialog, speech):
		dialog.current.speeches.append(dialog.get_for(self.config["id"]))
		dialog.current.rebuild_text()
		debug("Showed speech "+self.config["id"])

def init_primitives(root, console):
	primitives.register_primitive(root, "show_speech", ShowSpeech)