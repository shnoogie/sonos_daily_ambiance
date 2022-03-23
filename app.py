from apscheduler.schedulers.blocking import BlockingScheduler
import random, time, datetime, soco
import config

def get_track(device, track_type):
    if track_type == 'random': 
        # get all the tracks in the album
        tracks = device.music_library.get_albums('albums', subcategories=[config.audio_data['album']])
        track_list = []
        
        blacklist = config.track_blacklist

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

def get_devices(start=True):
    # create an empty list for devices to populate into
    devices = list(soco.discover())
    if start:
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
    else: # get current renewed list because things can change
        device_list = []
        members = []
        audio_data = config.audio_data
        coordinator = None
        i = 0
        while 2 > i:
            for device in devices:
                track_info = device.get_current_track_info()
                if track_info['artist'] == audio_data['artist'] and track_info['album'] == audio_data['album']:
                    coordinator = device
                    device_list.append(device)
                    members = list(device.group.members)
                else:
                    if members:
                        if device in members:
                            if device not in device_list:
                                device_list.append(device)
            i += 1

    return device_list, coordinator

def ajust_volume(on):
    devices, coordinator = get_devices(start=False)
    if on is True:
        volume = config.base_volume
        for device in devices:
            device.ramp_to_volume(volume, ramp_type='ALARM_RAMP_TYPE')
    elif on is False:
        volume = 0
        for device in devices:
            device.ramp_to_volume(volume, ramp_type='ALARM_RAMP_TYPE')

def generate_schedule():
    end_date = '{} 20:00:00'.format(datetime.date.today())

    # remove jobs and start again
    for job in scheduler.get_jobs():
        job.remove()

    # add the weather scheduler
    scheduler.add_job(generate_schedule, 'cron', hour=1, minute=0)

    # get the fixed schedules added
    for event in config.schedule:
        hour = config.schedule[event]['start']
        scheduler.add_job(start_ambiance, 'cron', [event], hour=hour, minute=0)
        #create a stop job
        end_hour = hour + config.schedule[event]['duration']
        scheduler.add_job(stop_ambiance, 'cron', hour=end_hour, minute=0)


    # generate weather events
    events = []
    event_count = random.randrange(config.event_range[0], config.event_range[1])
    high = config.schedule['evening']['start'] - 1
    low = config.schedule['morning']['start'] + 1
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
        hour = int(event[0])
        minute = int(event[1])
        # add some entropy, humans crave that
        if minute < 30:
            minute = minute + random.randint(1,29)
        elif minute == 30:
            minute = minute + random.randint(1,20)

        scheduler.add_job(start_ambiance, 'cron', ['random'], hour=hour, minute=minute, end_date=end_date)

    scheduler.print_jobs()

def stop_ambiance():
    current_time = datetime.datetime.today().strftime('%H:%M')
    print('Stopping - {}'.format(current_time))
    devices, coordinator = get_devices(start=False)
    ajust_volume(False)
    time.sleep(15)
    if coordinator:
        coordinator.stop()

def generate_timestamps(track_duration):
    now = datetime.datetime.now().timestamp()

    play_duration = '00:{}:00'.format(random.randrange(config.duration[0], config.duration[1]))
    play_duration = time.strptime(play_duration,'%H:%M:%S')
    play_duration = datetime.timedelta(hours=play_duration.tm_hour,minutes=play_duration.tm_min,seconds=play_duration.tm_sec).total_seconds()

    track_duration = time.strptime(track_duration,'%H:%M:%S')
    track_duration = datetime.timedelta(hours=track_duration.tm_hour,minutes=track_duration.tm_min,seconds=track_duration.tm_sec).total_seconds()

    start_max = track_duration - play_duration
    start_time = 0

    # if the track time is shorter then the max potental play time then start from 0
    if track_duration > config.duration[1]*60: # convert to minutes
        start_time = random.randrange(0, start_max)
    else:
        start_time = 0

    stop_time = now + play_duration
    
    stop_time = datetime.datetime.fromtimestamp(stop_time)
    stop_time = [stop_time.hour, stop_time.minute]

    start_time = str(datetime.timedelta(seconds=start_time))
    play_duration = str(datetime.timedelta(seconds=play_duration))
    
    return start_time, stop_time


def start_ambiance(track_type):
    current_time = datetime.datetime.today().strftime('%H:%M')
    print('Running {} on {}'.format(track_type, current_time))
    # create an instance of all sonos devices
    devices, coordinator = get_devices()

    if coordinator is None:
        print('No speakers available. Exiting.')
        exit()

    # get the queue ready, select and add track
    coordinator.clear_queue()
    track = get_track(coordinator, track_type)
    coordinator.add_to_queue(track)

    # select random position to start based on track duration
    track_info = coordinator.get_current_track_info()
    start_time, stop_time = generate_timestamps(track_info['duration'])

    print('Adding stop schedule for {} on {}:{}'.format(track_type, stop_time[0], stop_time[1]))
    scheduler.add_job(stop_ambiance, 'cron', hour=stop_time[0], minute=stop_time[1])

    # there should only be 1 track on the queue
    coordinator.play_from_queue(index=0)
    coordinator.seek(start_time)

    # set volume
    ajust_volume(True)


if __name__ == '__main__':
    try:
        scheduler = BlockingScheduler(timezone=config.timezone)
    except Exception as e:
        print(e)
        exit()

    # generate first set of random weather
    generate_schedule()

    if config.run_on_start:
        start_ambiance('random')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        stop_ambiance()
