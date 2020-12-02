from apscheduler.schedulers.blocking import BlockingScheduler
import random, time, datetime, soco
import config

def get_track(device, track_type):
    if track_type == 'random': 
        # get all the tracks in the album
        tracks = device.music_library.get_albums('albums', subcategories=[config.audio_data['album']])
        track_list = []
        
        # blacklisting static sounds
        # blacklist = [ config.schedule[item]['track'] for item in config.schedule ]
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

def generate_schedule(first=False):
    end_date = '{} 20:00:00'.format(datetime.date.today())

    # remove jobs and start again
    for job in scheduler.get_jobs():
        job.remove()

    if first is True:
        # job will start when first launched, create a job to end it
        # get current hour and minute
        hour = datetime.datetime.today().hour
        minute = datetime.datetime.today().minute
        hour, minute = calculate_duration(hour, minute)
        scheduler.add_job(stop_ambiance, 'cron', hour=hour, minute=minute, end_date=end_date)

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
        hour = int(event[0])
        minute = int(event[1])
        # add some entropy, humans crave that
        if minute < 30:
            minute = minute + random.randint(1,29)
        elif minute == 30:
            minute = minute + random.randint(1,20)

        stop_hour, stop_minute = calculate_duration(hour, minute)

        scheduler.add_job(start_ambiance, 'cron', ['random'], hour=hour, minute=minute, end_date=end_date)
        scheduler.add_job(stop_ambiance, 'cron', hour=stop_hour, minute=stop_minute, end_date=end_date)

    scheduler.print_jobs()

def calculate_duration(hour, minute):
# caclulate the new timestamp based on duration from config
    ambiance_duration = config.duration
    minute = minute + ambiance_duration
    if minute >= 60:
        hour = hour + 1
        remainder = minute % 60
        if remainder >= 60:
            minute = remainder - 60
        else:
            minute = remainder

    return hour, minute

def stop_ambiance():
    current_time = datetime.datetime.today().strftime('%m/%d/%Y %H:%M')
    print('Stopping at {}'.format(current_time))
    devices, coordinator = get_devices(start=False)
    ajust_volume(False)
    time.sleep(15)
    if coordinator:
        coordinator.stop()

def start_ambiance(track_type):
    current_time = datetime.datetime.today().strftime('%m/%d/%Y %H:%M')
    print('Starting {} at {}'.format(track_type, current_time))
    # create an instance of all sonos devices
    devices, coordinator = get_devices()

    if coordinator is None:
        print('No speakers available. Exiting.')
        exit()

    # get track durations
    if track_type == 'random':
        duration = config.duration
    else:
        duration = config.schedule[track_type]['duration']

    # get the queue ready, select and add track
    coordinator.clear_queue()
    track = get_track(coordinator, track_type)
    coordinator.add_to_queue(track)

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

    # set volume
    ajust_volume(True)

    ######
    # Old way to have stop ambiance
    ######

    # play ambiance for desired time
    #try:
    #    time.sleep(duration-60)
    #except (KeyboardInterrupt, SystemExit):
    #    stop_ambiance()
    #    exit()

    #devices, coordinator = get_devices()

    #stop_ambiance()

    # let the volume fade out before stopping
    #print('Stopping: {}'.format(track_type))
    #time.sleep(60)
    #coordinator.stop()

if __name__ == '__main__':
    scheduler = BlockingScheduler()

    # generate first set of random weather
    #start_ambiance('evening')
    generate_schedule(first=False)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        stop_ambiance()