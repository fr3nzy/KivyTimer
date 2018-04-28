from kivy.app import App
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader


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
			

class SetTime(Popup):	
	def __init__(self):
		super(SetTime, self).__init__()
		
		self.txt_input = TextInput(hint_text='hh:mm:ss', multiline=False) 
		confirm_btn = Button(text='Confirm')
		confirm_btn.bind(on_press=self.confirm_btn_press)
		
		boxlayout = BoxLayout(orientation='vertical', spacing=8, padding=(0,8,0,0))
		boxlayout.add_widget(self.txt_input)
		boxlayout.add_widget(confirm_btn)
		
		self.popup = Popup(title='Set time period', content=boxlayout, size_hint=(.7, .25))
	
	def load_popup(self):
		self.popup.open()
	def close_popup(self):	
		self.popup.dismiss()
	
	def confirm_btn_press(self, widget):
		app = App.get_running_app()
		app.root.ids.time.text = self.txt_input.text
		
		total_seconds = ((int(self.txt_input.text[0]+  self.txt_input.text[1])*60*60) + 
										(int(self.txt_input.text[3] + self.txt_input.text[4])*60) +
										(int(self.txt_input.text[6] + self.txt_input.text[7])))
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
