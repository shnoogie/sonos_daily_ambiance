import os, yaml

# check for dev
if os.path.exists('DEV'):
    DEV = True
else:
    DEV = False

# default timezone
if os.environ.get('TZ'):
    timezone = os.environ.get('TZ')
else:
    timezone = "UTC"

# schedule to run after start
if os.environ.get('APP_RUNONSTART') == "True":
    run_on_start = True
else:
    run_on_start = False

if DEV:
    run_on_start = True

# schedule to run after start
if os.environ.get('APP_CONFIG'):
    config_file = 'config/{}'.format(os.environ.get('APP_CONFIG'))
else:
    config_file = 'config/config.yaml'

with open(config_file, 'r') as yamlfile:
    yaml_config = yaml.load(yamlfile, Loader=yaml.FullLoader)

album = yaml_config['ambiance settings']['album']
artist = yaml_config['ambiance settings']['artist']
duration_range = yaml_config['ambiance settings']['duration range']
event_range = yaml_config['ambiance settings']['event range']
base_volume = yaml_config['ambiance settings']['volume']
operation_time = yaml_config['ambiance settings']['operation time']
port = yaml_config['ambiance settings']['port']

# Optionals
if 'track blacklist' in yaml_config:
    track_blacklist = yaml_config['track blacklist']
else:
    track_blacklist = None

if 'device settings' in yaml_config:
    device_settings = yaml_config['device settings']
else:
    device_settings = None

if 'schedule' in yaml_config:
    schedule = yaml_config['schedule']
else:
    schedule = None

if 'track weight' in yaml_config:
    track_weight = yaml_config['track weight']
else:
    track_weight = None
