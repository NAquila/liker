import yaml
from os.path import dirname, join
from logging.config import dictConfig
from datetime import datetime
from os.path import expanduser, join

module_file = dirname(__file__)
logging_file = join(module_file, 'logging_config.yaml')
credentials_file = join(module_file, 'credentials.yaml')

# Set-up logging
with open(logging_file, 'r') as f:
    log_conf = yaml.safe_load(f)

log_filepath = join(expanduser('~'), logs, liker)
log_filepath += datetime.now().strftime('y/m/d/hm') + '.log'
log_conf['handlers']['h_file']['filename'] = log_filepath
dictConfig(log_conf)    
