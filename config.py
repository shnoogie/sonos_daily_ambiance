# how long a random event should last
duration = 1800 # 30 min
# how many events occur in a day
event_range = [6, 8]
# select volume
volume = 30

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