# how long a random event should last
duration = 1800 # 30 min
# how many events occur in a day
event_range = [6, 8]
# select volume
volume = 30

# soco doesn't always audo discover depending on your network
# I opted to use static ips.
# if useage is true, play anyways
devices = {
    'tv_room': {
        'ip': '192.168.5.232',
        'volume': 15,
        'if_used': True
        },
    'kitchen': {
        'ip': '192.168.5.52',
        'volume': 25,
        'if_used': False
        },
    'playroom': {
        'ip': '192.168.5.174',
        'volume': 25,
        'if_used': False
        },
    'bedroom': {
        'ip': '192.168.5.35',
        'volume': 25,
        'if_used': False
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