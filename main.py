# SoundLoader doesnt seem to work, maybe use some sort of external library to play sound
# check to see if time between reminders really is reminder

from kivy.core.audio import SoundLoader
from jnius import autoclass

SystemClock = autoclass('android.os.SystemClock')


for i in range(30):
	print('service started')

with open('content/total_time_set', 'r') as f:
	current_total = int(f.read())
	
# countdown timer
# count down the seconds, alarm every x seconds, final alarm end of seconds, check every second to see if playing? has changed

with open('content/reminder', 'r') as f:
	reminder = int(f.read()) #str - could be secs or 'none'
		
for i in range(current_total):
	SystemClock.sleep(1000)
	current_total-=1
	
	# reminder alarm -> self.reminder after self.reminder has passed -> (seconds_set - (seconds_set - seconds_passed)) - reminder_value
	try: 
		with open('content/total_time_set', 'r') as f: 
			total_seconds = int(f.read())
		if (((total_seconds - current_total) == reminder and current_total is not 0)): # not 0 to avoid conflicts with main alarm 
			with open('content/total_time_set', 'w') as f: 
				f.write(str(total_seconds - reminder))
			for i in range(100):
				SystemClock.sleep(100)
				print('reminder')
			reminder_bell = SoundLoader.load('content/Bell1.wav')
			reminder_bell.play()
	except Exception as e: # reminder is 'none'
		print(e)
		
#	if current_total == 0: # countdown ended
#		alarm = SoundLoader.load('content/meditation_tone.wav')
#		alarm.play()
#		self.app.root.ids.play_pause.source = 'img/play.png'
#		with open('content/playing?', 'w') as f:
#			f.write('no')'''
