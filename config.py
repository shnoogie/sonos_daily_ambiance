# range of time for a track to place
duration = [15, 30] #whole numbers in min

# how many events occur in a day
event_range = [8, 12]
# select volume
base_volume = 40

# tracks to ignore in random, can be added in fixed schedule
track_blacklist = ['Night']

# fixed schedule, what time it starts and what track to use.
schedule = {
    'morning': {
        'start': 7, # 7am
        'track': 'Birds',
        'duration': 1 # 3 hours
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
    'album': 'Home',
    'artist': 'Ambiance'
}