import yaml
from os.path import dirname, join
from logging.config import dictConfig

module_file = dirname(__file__)
logging_file = join(module_file, 'logging_config.yaml')
credentials_file = join(module_file, 'credentials.yaml')

# Set-up logging
with open(logging_file, 'r') as f:
    log_conf = yaml.safe_load(f)
dictConfig(log_conf)    
