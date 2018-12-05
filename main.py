from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'width', 450)
Config.set('graphics', 'height', 650)
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

import re


class Timer:
	def start(self):
		self.app = App.get_running_app()
		# countdown timer
		self.time = self.app.root.ids.time.text # time label
		self.hours = int(self.time[0] + self.time[1]) # xx:00:00
		self.minutes = int(self.time[3] + self.time[4]) # 00:xx:00
		self.seconds = int(self.time[6] + self.time[7])  # 00:00:xx
		
		self.current_total = (self.hours*60*60) + (self.minutes*60) + (self.seconds) # total seconds
		reminder_text = self.app.root.ids.reminder_spinner.text
		if reminder_text not in 'Remind every.. [Off]':
			if reminder_text[2] == 'm' or reminder_text[3] == 'm':	# 1 or 2 digit number 'm'inutes
				self.reminder = int(reminder_text[0] + reminder_text[1]) * 60  # to seconds
			else: # 's'econds
				self.reminder = int(reminder_text[0] + reminder_text[1])
		
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
		
		self.current_total -= 1 
		self.seconds -= 1 
		self.app.root.ids.timer_progress.value += 1
		
		def label_format(data): # add '0' before time if only 1 digit present (below 10)
			return str(data) if len(str(data)) == 2 else '0' + str(data)
		
		# reminder alarm -> self.reminder after self.reminder has passed -> (seconds_set - (seconds_set - seconds_passed)) - reminder_value
		try: 
			with open('content/total_time_set', 'r') as f: 
				total_seconds = int(f.read())
			if (((total_seconds - self.current_total) == self.reminder and self.current_total is not 0)): # not 0 to avoid conflicts with main alarm 
				with open('content/total_time_set', 'w') as f: 
					f.write(str(total_seconds - self.reminder))
				reminder_bell = SoundLoader.load('content/Bell1.wav')
				reminder_bell.play()
		except Exception as e:
			print(e)
		
		# update label	
		self.app.root.ids.time.text = label_format(self.hours) + ':' + label_format(self.minutes) + ':' + label_format(self.seconds)
		
		if self.seconds == 0 and self.minutes == 0 and self.hours == 0: # countdown ended
			alarm = SoundLoader.load('content/meditation_tone.wav')
			alarm.play()
			self.app.root.ids.play_pause.source = 'img/play.png'
			self.stop()	
		
	def stop(self):
		self.clock_event.cancel()
		
		
class CustomInput(TextInput):
	def insert_text(self, string, from_undo=False):
		if len(self.text) == 2 and re.compile('0\\d').search(self.text) is None: # is xx already present?
			return # don't allow any more chars to be entered if first digit is not 0
			
		if re.compile('\\d').search(string): # is inputted char a digit 0-9? 			
			if self.text == '':
				self.text = '0' + string # add 0 before to keep formatting after simple	
				return
			if re.compile('0\\d').search(self.text): # format is 0x?
				if re.compile('0[0-5]').search(self.text) is None: # format of 2nd char more than 0-5?
					self.text = '0' + string # remove the original 2nd char as format can't be more than '59'
				else:	 # format of 2nd char IS 0-5
					self.text = self.text[-1] + string # remove leading zero
			else: # if backspace and self.text is 1 char
				self.text = self.text + string
				return 
			
			

class SetTime(Popup):	
	def __init__(self):
		super(SetTime, self).__init__()
		
		self.app = App.get_running_app()
		
		# size of widgets must be in relation to window size. since most phones have similar screen proportions, you just need to ensure that the widgets are scaled in proportion to the entire window
		# the user wont be changing the actual window size, just the pixel density will change across devices, so you just need to ensure that what look aesthetically pleasing for one phone sized window is created based on window size.
		self.hrs_input = CustomInput(hint_text='hh', multiline=False, size_hint=(None,None), \
											size=(self.app.root.width/16,self.app.root.height/22))
		self.hrs_input.pos = (self.app.root.width / 2.35) - (self.hrs_input.width / 2), \
									(self.app.root.height / 2) - (self.hrs_input.height / 2)
		self.min_input = CustomInput(hint_text='mm', multiline=False, size_hint=(None,None), \
											size=(self.app.root.width/16,self.app.root.height/22)) 
		self.min_input.pos = (self.app.root.width / 2) - (self.min_input.width / 2), \
									(self.app.root.height / 2) - (self.min_input.height / 2)
		self.sec_input = CustomInput(hint_text='ss', multiline=False, size_hint=(None,None), \
											size=(self.app.root.width/16,self.app.root.height/22)) 
		self.sec_input.pos = (self.app.root.width / 1.75) - (self.sec_input.width / 2), \
									(self.app.root.height / 2) - (self.sec_input.height / 2)
		
		self.input_layout = FloatLayout(size_hint_x=None)
		self.input_layout.add_widget(self.hrs_input)
		self.input_layout.add_widget(self.min_input)
		self.input_layout.add_widget(self.sec_input)
		
		confirm_btn = Button(text='Confirm', size_hint=(None,None))
		confirm_btn.size = ((self.app.root.width / 1.55), (self.app.root.height / 14))
		confirm_btn.pos = ((self.app.root.width / 2) - (confirm_btn.width / 2), \
									(self.app.root.height / 2.35) - (confirm_btn.height / 2))
		confirm_btn.bind(on_press=self.confirm_btn_press)
		
		boxlayout = FloatLayout()
		boxlayout.add_widget(self.	input_layout)
		boxlayout.add_widget(confirm_btn)
		
		self.popup = Popup(title='Set time period', content=boxlayout, size_hint=(.7, .25))

	
	def load_popup(self):
		self.popup.open()
	def close_popup(self):	
		self.popup.dismiss()
	
	def confirm_btn_press(self, widget):
		app = App.get_running_app()
		app.root.ids.time.text = ':'.join(map(str.strip, [self.hrs_input.text, self.min_input.text, self.sec_input.text]))
		print(':'.join(map(str.strip, [self.hrs_input.text, self.min_input.text, self.sec_input.text])))
		
		total_seconds = (int(self.hrs_input.text)*60*60) + (int(self.min_input.text)*60) + int(self.sec_input.text)
		with open('content/total_time_set', 'w') as f:  # total_seconds must not be dependent on play_pause
			f.write(str(total_seconds))
		
		app.root.ids.timer_progress.max = total_seconds 
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
			

class ResetButton(Button):
	def on_press(self):
		app = App.get_running_app()
		if app.root.ids.play_pause.source == 'img/play.png':
			app.root.ids.time.text = '00:00:00'
			app.root.ids.timer_progress.value = 0


class BreathTimer(App):
	def build(self):
		return Builder.load_file('design.kv')
		
		
BreathTimer().run()
