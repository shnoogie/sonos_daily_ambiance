# sonos_daily_ambiance
This app schedules random daily ambiance events using sonos. Fixed schedules can also be created, wake up to bird songs. You can randomly determine how many events in a day and where the track starts to keep from being fatigued. You can easily add new tracks without the need to update config.

# to do
 - device monitoring and grouping while track is playing
 - configuration error handling
 - add simple web interface for stats and manual start

# configuration
Some configuration settings are set through enviromental variables.

- TZ - set the timezone using TZ database names seen here https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. default: UTC
- APP_RUNONSTART - runs an event when the app is started. default: False
- APP_CONFIG - sets name of configuration file. default: config.yaml

Others are set in config/config.yaml. Example:
```
# All settings in 'ambiance settings' are required
ambiance settings:
  album: Home
  artist: Ambiance
  duration range: # Sets the range for a track duration in minutes
  - 15
  - 30
  event range: # Sets the range for number of events to be played in a day
  - 8
  - 12
  volume: 30 # Sets the base volume
  operation time: # Sets the time window where events will be played
    start: 9
    end: 20

# The follow settings are optional
device settings: # Per device settings, using the Sonos player's name
  TV Room:
    volume: 20 # Sets custom volume levels for the device
  Baby Room:
    enabled: False # Removes the device from the automation
schedule: # Sets a custom schedule for static events
  evening:
    duration: 1 # Required. Length of event in hours
    start: 20 # Required. Time to start the event
    track: Night # Required. Track name to be used by event
    volume: 15 # WORK IN PROGRESS. Sets max volume of manual event
  morning:
    duration: 1
    start: 7
    track: Birds
track blacklist: # Tracks to be ignored when a random event is started
  -Night

```

# installation
```
git clone https://github.com/shnoogie/sonos_daily_ambiance.git
cd sonos_daily_ambiance
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
APP_RUNONSTART=True TZ=UTC python app.py
```

# docker
```
git clone https://github.com/shnoogie/sonos_daily_ambiance.git
cd sonos_daily_ambiance
docker build --no-cache -t "sonos_ambiance" .
docker run -d --network host --name "sonos_ambiance" -e "TZ=UTC" -e "APP_RUNONSTART=True" sonos_ambiance
```
