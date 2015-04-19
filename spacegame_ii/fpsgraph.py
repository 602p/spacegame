 # Permission is hereby granted, free of charge, to any person obtaining
 # a copy of this software and associated documentation files (the
 # "Software"), to deal in the Software without restriction, including
 # without limitation the rights to use, copy, modify, merge, publish,
 # distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so, subject to
 # the following conditions:
 
 # The above copyright notice and this permission notice shall be included
 # in all copies or substantial portions of the Software.
 
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 # IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 # CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 # TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pygame, datetime

### BEGIN USER CODE

#import absroot

FONT        = pygame.font.SysFont("monospace", 14)
DATASOURCES = (
#	(NAME,   COLOR,       DATASOURCE,                TYPE,                UPDATE, SCALE,       ARGS...)
	("FPS",  (0,0,255),   "absroot.clock.get_fps()", "RawDatasource",     0.02,     1 ),
	("S/S",  (0,255,0),   "absroot.game_time",       "DeltaDatasource",   0.5,      75, float),
	("EVT",  (255,0,0),   "absroot.last_events_len", "RawDatasource",     0.1,      10),
	("BLIT", (255,255,0), "absroot.screen.blits",    "DeltaDatasource",   0.5,      0.02),
	("TBLT", (255,0,255), "absroot.screen.tblits",   "DeltaDatasource",   0.5,      0.02)
)

KEYMOD    = pygame.KMOD_CTRL
KEYCODE   = pygame.K_F5
PAUSECODE = pygame.K_F6

GRAPH_RANGE  = (0, 100)
GRAPH_RECT   = pygame.Rect(0, 0, 1300, 150)
GRAPH_BG     = (255, 255, 255, 175)
GRAPH_UPDATE = 0.02

### END USER CODE

def _tuple_get(obj, pos, default=None):
	if len(obj) > pos:
		return obj[pos]
	return default

class RawDatasource(object):
	def __init__(self, config):
		self.name=config[0]
		self.color=config[1]
		self.datasource=config[2]
		self.type=config[3]
		self.update_time=config[4]
		self.scale=config[5]
		self.cast_type=_tuple_get(config, 6, int)
		self.name_img=FONT.render(self.name, 1, self.color)
		self.config=config
		self.last_data=0
		self.out_data=0
		self.cache_data=0
		self.cache_pos=0
		self.lastupdate=datetime.datetime.now()
		self._init()

	def _init(self):
		pass

	def fetch_data(self, namespace):
		self.last_data=eval(self.datasource, namespace)
		#

	def process_data_pre(self, namespace):
		pass
		#

	def process_data_post(self, namespace):
		self.out_data = self.last_data
		#

	def update(self, namespace):
		if datetime.datetime.now()-self.lastupdate>datetime.timedelta(seconds=self.update_time):
			self.process_data_pre(namespace)
			self.fetch_data(namespace)
			self.process_data_post(namespace)
			self.lastupdate=datetime.datetime.now()
			self.name_img=FONT.render(self.name+": "+str(self.cast_type(self.out_data)), 1, self.color)

	def render(self, image, pos):
		scaled_y=GRAPH_RECT.bottom-int(self.out_data*self.scale)
		pygame.draw.line(image, self.color, (self.cache_pos, self.cache_data), (pos, scaled_y), 2)
		self.cache_data=scaled_y
		self.cache_pos=pos

	def render_text(self, image, pos):
		image.blit(self.name_img, (pos, int(self.cache_data)))

class DeltaDatasource(RawDatasource):
	def process_data_pre(self, ns):
		self.pre_data=self.last_data

	def process_data_post(self, ns):
		self.out_data=(self.last_data-self.pre_data)/(datetime.datetime.now()-self.lastupdate).total_seconds()

processed_datasources = []
graph_image  = None
current_pos  = 0
last_update  = datetime.datetime.now()
graph_active = False
paused       = False

for dsconfig in DATASOURCES:
	processed_datasources.append(eval(dsconfig[3])(dsconfig))

def _reset_image():
	global graph_image
	graph_image = pygame.Surface(GRAPH_RECT.size).convert_alpha()
	graph_image.fill(pygame.Color(*GRAPH_BG))

_reset_image()

def update(namespace={}, **namespace_kw):
	global paused
	namespace.update(namespace_kw)
	if not paused:
		for datasource in processed_datasources:
			datasource.update(namespace)

def render(screen):
	global last_update, current_pos, paused
	if graph_active:
		screen.blit(graph_image, GRAPH_RECT)
		for datasource in processed_datasources:
				datasource.render_text(screen, current_pos)
		if datetime.datetime.now()-last_update>datetime.timedelta(seconds=GRAPH_UPDATE) and not paused:
			for datasource in processed_datasources:
				datasource.render(graph_image, current_pos)

			last_update=datetime.datetime.now()
			current_pos+=1
			if current_pos > GRAPH_RECT.width:
				current_pos=0
				for datasource in processed_datasources:
			 		datasource.cache_pos=0
			 		datasource.cache_data=0
				_reset_image()
		

		

def event(events):
	global graph_active, paused
	for e in events:
		if e.type==pygame.KEYDOWN:
			if e.mod & KEYMOD:
				if e.key == KEYCODE:
					graph_active = not graph_active
				if e.key == PAUSECODE:
					paused = not paused