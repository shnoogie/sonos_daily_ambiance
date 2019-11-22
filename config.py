# how long a random event should last
duration = 1800 # 30 min
# how many events occur in a day
event_range = [6, 8]
# select volume
volume = 30

# soco doesn't always audo discover depending on your network
# I opted to use static ips.
devices = {
    'family_room': {
        'ip': '192.168.5.203',
        'volume': 30
        },
    'kitchen': {
        'ip': '192.168.5.14',
        'volume': 30
        },
    'playroom': {
        'ip': '192.168.5.51',
        'volume': 50
        },
    'bedroom': {
        'ip': '192.168.5.33',
        'volume': 15
        }
}
# fixed schedule, what time it starts and what track to use.
schedule = {
    'morning': {
        'start': 7,
        'track': 'Birds',
        'duration': 7200 # 3 hours
    },
    'evening': {
        'start': 20, # 8pm
        'track': 'Night',
        'duration': 3600 # 1 hour
    }
}

# this app uses sonos audio library for tracks
# to ensure we get correct tracks have album and artist
audio_data = {
    'album': 'Nature Sounds',
    'artist': 'Ambiance'
}