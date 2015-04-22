import assets, absroot, random, tasks, state
import triggers, extention_loader, pygame

class MusicTrack(object):
	def __init__(self, node, basepath, metadata={}): #Called right from asset loader
		assert "sound" in node, "Assets of type `track` require a `sound` attribute"
		self.sound=absroot.gamedb(node["sound"])
		self.tags=node.get("tags",[])
		self.affinities=node.get("affinity",{})
		self.threshold=node.get("threshold", 2)
		self.priority=float(node.get("priority", 1))
		self.name=node.get("trackname", node["sound"])
		self.decay=node.get("decay", node.get("decay", 0.1))
		self.value=0.0
		absroot.music_tracks.append(self)

	def on_event(self, event):
		if triggers.IS_SG_EVENT(event):
			if event.sg_type in self.affinities:
				# print "Got a "+event.sg_type+": "+self.name+".value+="+str(self.affinities[event.sg_type])
				self.value+=self.affinities[event.sg_type]
		self.value=max(self.value, 0)

	def tick(self):
		self.value-=(1.0/absroot.fps)*self.decay

	def get_value(self):
		x=(self.value * self.priority)
		# if self in get_manager().recent_plays:
		# 	x -= get_manager().recent_plays.index(self)
		return x

@extention_loader.hook_extention("music_manager")
class MusicManager(extention_loader.HookableExtention):
	name="Music Controller"
	get_desc=lambda s:"Controls the switching of Music"

	def _init(self):
		self.channel=pygame.mixer.Channel(1)
		self.old_top=None
		self.recent_plays=[]
		self.playing_requested=True
		self.current_track=None

	def last_load(self):
		absroot.state_manager.factories["music_debug"]=state.InterdictingStateFactory(MusicDebugState)

	def event_root(self, event):
		for track in absroot.music_tracks:
			track.on_event(event)
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_F11:
				absroot.state_manager.start_interdicting("music_debug")

	def tick(self, state):
		if state=="game":
			for track in absroot.music_tracks:
				track.tick()

			if not self.playing_requested:
				self.play_auto()
			else:
				if not self.channel.get_busy():
					self.playing_requested=False

	def stop(self):
		if self.channel.get_busy():
			self.channel.stop()

	def play(self, track):
		self.stop()
		self.current_track=track
		tasks.display_hanging_message("You are now listening to "+track.name+"", time=5, color=(100,255,100))
		self.channel.play(track.sound, fade_ms=1000)

	def play_tagged(self, tag):
		options=[]
		for track in absroot.music_tracks:
			if tag in track.tags:
				options.append(track)
		if options:
			self.play(random.choice(options))
			self.playing_requested=True
		else:
			tasks.display_hanging_message("play_tagged cannot find anything tagged `"+tag+"`", color=(255,0,0))

	def get_top_track(self):
		v=None
		a=[]
		for track in sorted(absroot.music_tracks, key=lambda t:-t.get_value()):
			if v==None:
				v=track.get_value()

			if track.get_value()!=v:
				return random.choice(a)
			else:
				a.append(track)

	def play_auto(self):
		t=self.get_top_track()
		if (t != self.current_track and (self.current_track is None or self.current_track.get_value()<t.get_value())) or not self.channel.get_busy():
			if self.current_track:
				self.recent_plays.insert(0, self.current_track)
				#self.recent_plays=[self.recent_plays[0]]
			self.play(t)

class MusicDebugState(state.InterdictingState):
	def first_start(self):
		self.basepos=0

	def internal_update(self):
		absroot.screen.screen.fill((0,0,0))
		pos=self.basepos
		for track in absroot.music_tracks:
			absroot.screen.screen.blit(absroot.gamedb("LOADER_font_plugin_list").render(track.name+": "+str(track.get_value()), 1, (255,255,255)), [0, pos])
			pos+=absroot.gamedb("LOADER_font_plugin_list").size("A")[1]
		absroot.screen.screen.blit(absroot.gamedb("LOADER_font_plugin_list").render("Top Track => "+get_manager().get_top_track().name+" (Value:"+str(get_manager().get_top_track().get_value())+")", 1, (255,255,255)), [0, pos])
		pos+=absroot.gamedb("LOADER_font_plugin_list").size("A")[1]
		absroot.screen.screen.blit(absroot.gamedb("LOADER_font_plugin_list").render("recent_plays => "+str([x.name for x in get_manager().recent_plays]), 1, (255,255,255)), [0, pos])
		pos+=absroot.gamedb("LOADER_font_plugin_list").size("A")[1]
		absroot.screen.screen.blit(absroot.gamedb("LOADER_font_plugin_list").render("playing_requested => "+str(get_manager().playing_requested), 1, (255,255,255)), [0, pos])

	def process_events(self, events):
		for e in events:
			if e.type==pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					self.finish()
			if e.type==pygame.MOUSEBUTTONDOWN:
				if e.button==5:
					self.basepos+=20
				if e.button==4:
					self.basepos-=20

def init():
	absroot.music_tracks=[]
	absroot.gamedb.register_loader("track", MusicTrack)

def get_manager():
	return absroot.extentions['music_manager']