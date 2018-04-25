from kivy.app import App
from kivy.lang.builder import Builder
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from time import sleep

Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '600')


class Timer:

	def start(self):
		self.app = App.get_running_app()
		# countdown timer
		self.time = self.app.root.ids.time.text # time label
		self.hours = int(self.time[0] + self.time[1]) # xx:00:00
		self.minutes = int(self.time[-5] + self.time[-4]) # 00:xx:00
		self.seconds = int(self.time[-2] + self.time[-1])  # 00:00:xx
		
		total_seconds = (self.hours*60*60) + (self.minutes*60) + (self.seconds)
		self.app.root.ids.timer_progress.max = total_seconds # max value for ProgressBar

		self.clock_event = Clock.schedule_interval(self.update_time, 1) # call every second
				
	def update_time(self, dt): 
		if self.seconds == 0:
			if self.minutes > 0:
				self.minutes -= 1
				self.seconds = 60
			elif self.hours > 0:
				self.hours -= 1
				self.minutes = 59
				self.seconds = 60
			else: # if play is pressed when 00:00:00
				self.app.root.ids.play_pause.source = 'img/play.png'
				return self.stop()
				
		
		self.seconds -= 1 
		self.app.root.ids.timer_progress.value += 1
		
		def label_format(data): # add '0' before time if only 1 digit present (below 10)
			return str(data) if len(str(data)) == 2 else '0' + str(data)
		
		# update label	
		self.app.root.ids.time.text = label_format(self.hours) + ':' + label_format(self.minutes) + ':' + label_format(self.seconds)
		
		if self.seconds == 0 and self.minutes == 0 and self.hours == 0: # countdown ended
			self.stop()	
		
	def stop(self):
		self.clock_event.cancel()
			

class SetTime(Popup):
	def __init__(self):
		super(SetTime, self).__init__()
		
		self.txt_input = TextInput(hint_text='hh:mm:ss', multiline=False) 
		time_btn = Button(text='Confirm')
		time_btn.bind(on_press=self.btn_on_press)
		
		boxlayout = BoxLayout(orientation='vertical', spacing=8, padding=(0,8,0,0))
		boxlayout.add_widget(self.txt_input)
		boxlayout.add_widget(time_btn)
		
		self.popup = Popup(title='Set time period', content=boxlayout, size_hint=(.7, .25))
	
	def load_popup(self):
		self.popup.open()
	def close_popup(self):	
		self.popup.dismiss()
	
	def btn_on_press(self, widget):
		app = App.get_running_app()
		app.root.ids.time.text = self.txt_input.text
		app.root.ids.timer_progress.value = 0
		self.close_popup()


class ChangeButton(Button):
	def on_release(self):
		app = App.get_running_app()
		if app.root.ids.play_pause.source == 'img/play.png':
			SetTime().load_popup()
		
		
class PlayButton(Button, Timer):
	def on_press(self):
		app = App.get_running_app()
		if app.root.ids.play_pause.source == 'img/play.png':
			app.root.ids.play_pause.source = 'img/pause.png'
			self.start()
		else:
			app.root.ids.play_pause.source = 'img/play.png'
			self.stop()
			

class ResetButton(Button, Timer):
	def on_press(self):
		app = App.get_running_app()
		if app.root.ids.play_pause.source == 'img/play.png':
			app.root.ids.time.text = '00:00:00'
			app.root.ids.timer_progress.value = 0


class BreathTimer(App):
	def build(self):
		return Builder.load_file('design.kv')
		
		
BreathTimer().run()
