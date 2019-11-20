# how long the event should last
duration = 1800 # 30 min
# how many events occur in a day
event_range = [3, 5]
# select volume
volume = 30
# soco doesn't always audo discover depending on your network
# I opted to use static ips.
devices = {
	'family_room': '192.168.5.203',
	'kitchen': '192.168.5.14',
	'playroom': '192.168.5.51',
	'bedroom': '192.168.5.33'
}
# fixed schedule, what time it starts and what track to use.
schedule = {
	'morning': {
		'start': 6,
		'track': 'Birds'
	},
	'evening': {
		'start': 20, # 8pm
		'track': 'Night'
	}
}
# this app uses sonos audio library for tracks
# to ensure we get correct tracks have album and artist
audio_data = {
	'album': 'Nature Sounds',
	'artist': 'Ambiance'
}