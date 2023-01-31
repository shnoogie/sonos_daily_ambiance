from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Process, Pipe
import os
import random
import time
import datetime
import soco
import json
import config

CURRENT_SCHEDULE = ''


def get_track(device, track_type):
    if track_type == 'random': 
        # get all the tracks on the album
        tracks = device.music_library.get_albums('albums', subcategories=[config.album])
        track_list = []
        
        if config.track_blacklist:
            blacklist = config.track_blacklist
        else:
            blacklist = []

        if config.track_weight:
            track_weight = config.track_weight
        else:
            track_weight = {}

        for track in tracks:
            if track.title not in blacklist:
                track_list.append(track)

        temp_track_list = []
        for track in track_list:
            if track.title in track_weight:
                weight = track_weight[track.title]
                count = 1
                while count <= weight:
                    count += 1
                    temp_track_list.append(track)

        track_list = track_list + temp_track_list

        # select random track
        random_track = random.choice(track_list)

        return random_track
    else:
        selection = config.schedule[track_type]['track']
        album = config.album
        artist = config.artist
        track = device.music_library.search_track(artist, album=album, track=selection, full_album_art_uri=False)
        return track[0]


def check_blacklist(device):
    device_name = device.player_name
    if config.device_settings:
        if device_name in config.device_settings:
            if 'enabled' in config.device_settings[device_name]:
                if config.device_settings[device_name]['enabled'] is False:
                    return True
    return False


def create_group():
    devices = list(soco.discover())
    coordinator = None
    device_list = []

    for device in devices:
        group_coordinator = device.group.coordinator
        if group_coordinator.get_current_transport_info()['current_transport_state'] != 'PLAYING':
            if not check_blacklist(device):
                if not coordinator:
                    device.unjoin()
                    device.set_relative_volume(-100)
                    coordinator = device
                else:
                    device.unjoin()
                    device.set_relative_volume(-100)
                    device_list.append(device)

    for device in device_list:
        if device is not coordinator:
            device.join(coordinator)

    # this waits to return till the group is finished being created
    # with a limit of 10 seconds to prevent infinite loops
    if coordinator:
        i = 0
        while True: 
            devices, coordinator = get_devices(coordinator)
            if len(device_list) + 1 == len(devices):
                break
            elif i >= 10:
                break
            time.sleep(1)
            i += 1

    return coordinator


def get_devices(coordinator=None):
    devices = list(soco.discover())
    device_list = []
    album = config.album
    artist = config.artist

    if not coordinator:
        for device in devices:
            track_info = device.get_current_track_info()
            if track_info['artist'] == artist and track_info['album'] == album:
                group_coordinator = device.group.coordinator
                if group_coordinator.get_current_transport_info()['current_transport_state'] == 'PLAYING':
                    coordinator = device
                    break

    if not coordinator:
        return None, None

    for member in coordinator.group.members:
        if member.is_visible:
            if not check_blacklist(member):
                if member not in device_list:
                    device_list.append(member)

    return device_list, coordinator


def adjust_volume(starting, coordinator=None):
    if coordinator:
        devices, coordinator = get_devices(coordinator)
    else:
        devices, coordinator = get_devices()

    if not devices:
        return False

    if starting is True:
        if config.device_settings:
            device_settings = config.device_settings
        else:
            device_settings = []

        for device in devices:
            volume = config.base_volume
            device_name = device.player_name
            if device_name in device_settings:
                if 'volume' in device_settings[device_name]:
                    volume = device_settings[device_name]['volume']
            ramp_time = device.ramp_to_volume(volume, ramp_type='SLEEP_TIMER_RAMP_TYPE')
        return ramp_time
    elif starting is False:
        volume = 1
        for device in devices:
            ramp_time = device.ramp_to_volume(volume, ramp_type='SLEEP_TIMER_RAMP_TYPE')
        return ramp_time


def generate_schedule():
    global CURRENT_SCHEDULE
    CURRENT_SCHEDULE = []

    # remove jobs and start again
    for job in scheduler.get_jobs():
        job.remove()

    # add the event scheduler
    scheduler.add_job(generate_schedule, 'cron', hour=1, minute=0)

    events = []
    event_count = random.randrange(config.event_range[0], config.event_range[1])
    start = config.operation_time['start']
    end = config.operation_time['end']
    event_window = end - start
    event_buffer = round(event_window / event_count, 2)
    time_value = float(start)
    i = 0

    while i < event_count:
        x = str(time_value).split('.')
        time = [x[0], int(round(float('.'+x[1]) * 59, 0))]
        events.append(time)
        time_value += event_buffer
        i += 1
    for event in events:
        hour = int(event[0])
        minute = int(event[1])
        # add some entropy, humans crave that
        if minute < 30:
            minute = minute + random.randint(1, 29)
        elif minute == 30:
            minute = minute + random.randint(1, 20)

        log('Adding event {} at {}:{}'.format('random', hour, minute))
        CURRENT_SCHEDULE.append('{} at {}:{}'.format('random', hour, minute))
        scheduler.add_job(start_ambiance, 'cron', ['random'], hour=hour, minute=minute)

    if config.schedule:
        for event in config.schedule:
            hour = config.schedule[event]['start']
            log('Adding event {} at {}:00'.format(event, hour))
            CURRENT_SCHEDULE.append('{} at {}:00'.format(event, hour))
            scheduler.add_job(start_ambiance, 'cron', [event], hour=hour, minute=0)
            end_hour = hour + config.schedule[event]['duration']
            scheduler.add_job(stop_ambiance, 'cron', hour=end_hour, minute=0)
            event_count += 1

    log('Generated schedule. Created {} events'.format(event_count))


def stop_ambiance():
    log('Stopping')
    for job in scheduler.get_jobs():
        if 'stop_ambiance' in job.name:
            scheduler.remove_job(job.id)
            log('Stop Jobs Removed')

    devices, coordinator = get_devices()
    ramp_time = adjust_volume(False)
    time.sleep(ramp_time + 5)
    if coordinator:
        coordinator.stop()


def generate_timestamps(track_duration):
    now = datetime.datetime.now().timestamp()

    play_duration = '00:{}:00'.format(random.randrange(config.duration_range[0], config.duration_range[1]))
    play_duration = time.strptime(play_duration, '%H:%M:%S')
    play_duration = datetime.timedelta(hours=play_duration.tm_hour, minutes=play_duration.tm_min,
                                       seconds=play_duration.tm_sec).total_seconds()

    track_duration = time.strptime(track_duration, '%H:%M:%S')
    track_duration = datetime.timedelta(hours=track_duration.tm_hour, minutes=track_duration.tm_min,
                                        seconds=track_duration.tm_sec).total_seconds()

    start_max = track_duration - play_duration
    start_time = 0

    # if the track time is shorter than the max potential play time then start from 0
    if track_duration > config.duration_range[1]*60:  # convert to minutes
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
    log('Starting {}'.format(track_type))

    if track_type != 'random':
        log('Stopping other events for manually scheduled event')
        stop_ambiance()

    coordinator = create_group()

    if coordinator is None:
        log('No speakers available.')
        return None

    devices, coordinator = get_devices(coordinator)

    # get the queue ready, select and add track
    coordinator.clear_queue()
    track = get_track(coordinator, track_type)
    coordinator.add_to_queue(track)

    # select random position to start based on track duration
    track_info = coordinator.get_current_track_info()
    start_time, stop_time = generate_timestamps(track_info['duration'])

    # add stop event if the track is random
    if track_type == 'random':
        log('Adding stop event at {}:{}'.format(stop_time[0], stop_time[1]))
        track_log(track.title)
        log('Playing Track: {}'.format(track.title))
        scheduler.add_job(stop_ambiance, 'cron', hour=stop_time[0], minute=stop_time[1])

    # there should only be 1 track on the queue
    coordinator.play_from_queue(index=0)
    coordinator.seek(start_time)

    adjust_volume(True, coordinator=coordinator)


def change_track():
    log('Changing track')

    devices, coordinator = get_devices()

    if coordinator is None:
        log('No track currently playing.')
        return None

    ramp_time = adjust_volume(False)
    time.sleep(ramp_time + 1)

    # get the queue ready, select and add track
    coordinator.clear_queue()
    track = get_track(coordinator, 'random')
    coordinator.add_to_queue(track)

    track_info = coordinator.get_current_track_info()
    start_time, stop_time = generate_timestamps(track_info['duration'])

    # there should only be 1 track on the queue
    coordinator.play_from_queue(index=0)
    coordinator.seek(start_time)

    adjust_volume(True, coordinator=coordinator)


def log(message):
    current_time = datetime.datetime.today().strftime('%m/%d/%Y %H:%M')
    message = '{}: {}'.format(current_time, message)
    print(message)
    with open('log.txt', 'a') as file:
        file.write(message+'\n')


def track_log(track):
    log_file = 'track_log.json'
    current_time = datetime.datetime.today().strftime('%m/%d/%Y %H:%M')

    if not os.path.exists(log_file):
        with open(log_file, 'w') as file:
            file.write('{}')

    with open(log_file, 'r') as file:
        json_data = json.loads(file.read())

    with open(log_file, 'w') as file:
        if track in json_data:
            json_data.update({
                track: {
                    'count': json_data[track]['count']+1,
                    'last_played': current_time
                }
            })
        else:
            json_data.update({
                track: {
                    'count': 1,
                    'last_played': current_time
                }
            })

        file.write(json.dumps(json_data, sort_keys=True))


def start_web(conn):
    import cherrypy
    import web_interface

    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()+'/web')
        },
        '/style': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'style'
        }
    }

    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = config.port
    cherrypy.quickstart(web_interface.app(conn), '/', conf)


def web_command(command):
    if command == 'schedule':
        parent_conn.send(CURRENT_SCHEDULE)

    elif command == 'generate_schedule':
        generate_schedule()
        parent_conn.send(CURRENT_SCHEDULE)

    elif command == 'start':
        start_ambiance('random')

    elif command == 'stop':
        stop_ambiance()

    elif command == 'change_track':
        change_track()

    elif command == 'index':
        devices, coordinator = get_devices()
        current_track = "None"
        if coordinator:
            current_track = str(coordinator.get_current_track_info()['title'])

        parent_conn.send(current_track)
    else:
        print('Unknown Command')


if __name__ == '__main__':
    log('App starting.\nEnvironment: timezone={}, run_on_start={}'.format(config.timezone, config.run_on_start))
    try:
        scheduler = BackgroundScheduler(timezone=config.timezone)
    except Exception as e:
        log(e)
        exit()

    # generate first set of random weather
    generate_schedule()

    try:
        scheduler.start()

        # set up web thread and communications pipe
        parent_conn, child_conn = Pipe()
        web_service = Process(target=start_web, args=(child_conn,))
        web_service.start()

        if config.run_on_start:
            start_ambiance('random')

        while True:
            web_command(parent_conn.recv())

    except (KeyboardInterrupt, SystemExit):
        stop_ambiance()
