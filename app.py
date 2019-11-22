from soco import SoCo
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
import random, time
import config

def get_track(device, track_type):
    if track_type is 'random': 
        # get all the tracks in the album
        tracks = device.music_library.get_albums('albums', subcategories=[config.audio_data['album']])
        track_list = []
        
        # blacklisting static sounds
        blacklist = [ config.schedule[item]['track'] for item in config.schedule ]

        for track in tracks:
            if track.title not in blacklist:
                track_list.append(track)

        # select random track
        random_track = random.choice(track_list)
        return random_track
    else:
        selection = config.schedule[track_type]['track']
        album = config.audio_data['album']
        artist = config.audio_data['artist']
        track = device.music_library.search_track(artist, album=album, track=selection, full_album_art_uri=False)
        return track[0]

def get_devices():
    # create an empty list for devices to populate into
    devices = []
    volumes = {}
    # create an instance for all devices
    for device in config.devices:
        new_instance = SoCo(config.devices[device]['ip'])
        # adding volumes like this makes it so config does not need updated when 
        # devices are renamed
        volumes.update({ new_instance.player_name: config.devices[device]['volume'] })
        devices.append(new_instance)
    return devices, volumes

def get_status(devices):
    # check to see if any devices are in use, we don't want to play ambiance if anything is being used
    in_use = False
    for device in devices:
        if device.is_coordinator:
            if device.get_current_transport_info()['current_transport_state'] == 'PLAYING':
                in_use = True
    return in_use

def ajust_volume(devices, volumes):
    if volumes:
        for device in devices:
            volume = volumes[device.player_name]
            device.ramp_to_volume(volume, ramp_type='SLEEP_TIMER_RAMP_TYPE')
    else:
        volume = 0
        for device in devices:
            device.ramp_to_volume(volume, ramp_type='SLEEP_TIMER_RAMP_TYPE')

def get_events():
    # generate weather events
    end_date = '{} 20:00:00'.format(date.today())
    events = []
    event_count = random.randrange(config.event_range[0], config.event_range[1])
    high = config.schedule['evening']['start'] - 2
    low = config.schedule['morning']['start'] + 2
    duration = high - low
    padding = round(duration / event_count, 2)

    # get the timestamps of each event
    time_value = low
    i = 0
    while i < event_count:
        time_value += padding
        x = str(time_value).split('.')
        time = [x[0], int(round(float('.'+x[1]) * 59, 0))]
        events.append(time)
        i += 1

    for event in events:
        scheduler.add_job(main, 'cron', ['random'], hour=event[0], minute=event[1], jitter=900, end_date=end_date)

    scheduler.print_jobs()

def main(track_type):
    print('Starting: {}'.format(track_type))
    # create an instance of all sonos devices
    devices, volumes = get_devices()

    # get track durations
    if track_type == 'random':
        duration = config.duration
    else:
        duration = config.schedule[track_type]['duration']

    in_use = get_status(devices)

    # if no devices are in use, party time!
    if not in_use:
        # add all devices into a single group
        devices[0].partymode()
        for device in devices:
            if device.is_coordinator:
                # coordinator is the device that you'll use to control all devices
                coordinator = device
    else:
        # if a device is in use, just exit
        print('Sonos in use, exiting.')
        exit()

    # get the queue ready, select and add track
    coordinator.clear_queue()
    track = get_track(coordinator, track_type)
    coordinator.add_to_queue(track)

    # set volume
    ajust_volume(devices, volumes)

    # files are supposed to be 10 hours log, don't go past 5 hours
    # in case one isn't
    random_timestamp = '{}:{}:{}'.format(
            str(random.randrange(0, 5)).zfill(2), 
            str(random.randrange(0, 59)).zfill(2), 
            str(random.randrange(0, 59)).zfill(2)
        )

    # there should only be 1 track on the
    coordinator.play_from_queue(index=0)
    coordinator.seek(random_timestamp)

    # play ambiance for desired time
    time.sleep(duration-60)

    # Fade out volume
    ajust_volume(devices, None)

    # let the volume fade out before stopping
    time.sleep(60)
    coordinator.stop()

if __name__ == '__main__':
    scheduler = BlockingScheduler()

    # get the fixed schedules added
    for event in config.schedule:
        scheduler.add_job(main, 'cron', [event], hour=config.schedule[event]['start'], minute=0)

    # add the weather generator
    scheduler.add_job(get_events, 'cron', hour=1, minute=0)

    # generate first set of random weather
    get_events()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass