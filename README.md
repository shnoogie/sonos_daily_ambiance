# sonos_daily_ambiance
This app schedules random daily ambiance events using sonos. Fixed schedules can also be created, wake up to bird songs. You can randomly determine how many events in a day and where the track starts to keep from being fatigued. You can easily add new tracks without the need to update config.

# to do
 - device monitoring and grouping while track is playing.
 - customizations for devices by device name
 	- custom volumes
 	- blacklists

# settings
Some settings are configured through enviromental variables.

- TZ - set the timezone used by the app using TZ database name seen here https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
- APP_RUNONSTART - (True/False) runs an event when the app is started

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