# how long a random event should last
duration = 30 # 30 min
# how many events occur in a day
event_range = [6, 8]
# select volume
base_volume = 20

# tracks to ignore in random, can be added in fixed schedule
track_blacklist = [ 'Night']

# fixed schedule, what time it starts and what track to use.
schedule = {
    'morning': {
        'start': 7, # 7am
        'track': 'Birds',
        'duration': 3 # 3 hours
    },
    'evening': {
        'start': 20, # 8pm
        'track': 'Night',
        'duration': 1 # 1 hour
    }
}

# this app uses sonos audio library for tracks
# to ensure we get correct tracks have album and artist
audio_data = {
    'album': 'Nature Sounds',
    'artist': 'Ambiance'
}