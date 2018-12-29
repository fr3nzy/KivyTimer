from jnius import autoclass
from plyer import notification
import sqlite3


mplayer = autoclass('android.media.MediaPlayer')
SystemClock = autoclass('android.os.SystemClock')
mediaplayer = mplayer()


# open the file containing the time to continue off from
with open('content/current_total', 'r') as f:
	current_total = int(f.read())  # seconds
	
notification.notify(title='Countdown in progress', message='tap to open & swiiipe to close this annoying notifcation ;P', app_name='Mindful Timer', timeout=current_total, ticker='timer in progressn')
	
# get reminder 
with open('content/reminder', 'r') as f:
	reminder = int(f.read()) # seconds
	
conn = sqlite3.connect('content/saved_settings.db')
cursor = conn.cursor()
cursor.execute('SELECT end_tone_url FROM settings')
end_tone = cursor.fetchone()[0]
cursor.execute('SELECT remind_tone_url FROM settings')
remind_tone = cursor.fetchone()[0]

for i in range(current_total):
	SystemClock.sleep(950)
	print('\n\n\n\n\n\n'+str(current_total))
	current_total -= 1
	
	with open('content/total_time_set', 'r') as f:
		if reminder is not 0 and current_total is not 0:
			if int(f.read()) - current_total == reminder:
				mediaplayer.reset()
				mediaplayer.setDataSource(remind_tone)
				mediaplayer.prepare()
				mediaplayer.start()
	with open('content/current_total', 'w') as f:
		f.write(str(current_total))
		
	if current_total is 0: # end 
		mediaplayer.reset()
		mediaplayer.setDataSource(end_tone)
		mediaplayer.prepare()
		mediaplayer.start()
	
SystemClock.sleep(13000)
mediaplayer.release()
