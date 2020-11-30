import soco 
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
import random, time
import config

def get_track(device, track_type):
    if track_type == 'random': 
        # get all the tracks in the album
        tracks = device.music_library.get_albums('albums', subcategories=[config.audio_data['album']])
        track_list = []
        
        # blacklisting static sounds
        # blacklist = [ config.schedule[item]['track'] for item in config.schedule ]
        blacklist = config.blacklist

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
    devices = list(soco.discover())
    coordinator = None
    device_list = []
    #### if you want to select or whitelist rooms ####
    #temp_device = []
    #count = 0
    #for device in devices:
    #    player_name = device.player_name
    #    if player_name == 'Office':
    #        temp_device.append(devices[count])
    #    count += 1
    #return temp_device
    i = 0
    # run twice to ensure all non-grouped devices are added.
    while 2 > i:
        for device in devices:
            if device.is_coordinator:
                if device.get_current_transport_info()['current_transport_state'] != 'PLAYING':
                    if coordinator != device:
                        if not coordinator:
                            coordinator = device
                            device_list.append(device)
                        else:
                            device.join(coordinator)
                            device_list.append(device)
        i += 1

    return device_list, coordinator

def ajust_volume(devices, volume_type):
    if volume_type:
        volume = config.volume
        for device in devices:
            device.ramp_to_volume(volume, ramp_type='SLEEP_TIMER_RAMP_TYPE')
    else:
        volume = 0
        for device in devices:
            device.ramp_to_volume(volume, ramp_type='SLEEP_TIMER_RAMP_TYPE')

def generate_schedule():
    # remove jobs and start again
    for job in scheduler.get_jobs():
        job.remove()

    # add the weather scheduler
    scheduler.add_job(generate_schedule, 'cron', hour=1, minute=0)

    # get the fixed schedules added
    for event in config.schedule:
        scheduler.add_job(main, 'cron', [event], hour=config.schedule[event]['start'], minute=0)

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

def app_exit():
    audio_data = config.audio_data
    devices = list(soco.discover())
    for device in devices:
        track_info = device.get_current_track_info()
        if track_info['artist'] == audio_data['artist'] and track_info['album'] == audio_data['album']:
            device.stop()

def main(track_type):
    try:
        print('Starting: {}'.format(track_type))
        # create an instance of all sonos devices
        devices, coordinator = get_devices()

        # get track durations
        if track_type == 'random':
            duration = config.duration
        else:
            duration = config.schedule[track_type]['duration']

        # get the queue ready, select and add track
        coordinator.clear_queue()
        track = get_track(coordinator, track_type)
        coordinator.add_to_queue(track)

        # set volume
        ajust_volume(devices, True)

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

        devices = get_devices()

        current_devices = []
        for device in devices:
            if device.get_current_track_info()['artist'] == config.audio_data['artist']:
                current_devices.append(device)
                if device.is_coordinator:
                    coordinator = device

        # Fade out volume
        ajust_volume(current_devices, None)

        # let the volume fade out before stopping
        print('Stopping: {}'.format(track_type))
        time.sleep(60)
        coordinator.stop()
    except (KeyboardInterrupt, SystemExit):
        app_exit()

if __name__ == '__main__':
    scheduler = BlockingScheduler()

    # generate first set of random weather
    generate_schedule()

    main('random')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        exit()