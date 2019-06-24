

# Do necessary imports in a function to avoid cluttering up
# namespace
def init_logging():
    import yaml
    from logging.config import dictConfig
    from datetime import datetime
    from os.path import dirname, join, expanduser
    from os import makedirs

    module_file = dirname(__file__)
    logging_file = join(module_file, 'logging_config.yaml')
    with open(logging_file, 'r') as f:
        log_conf = yaml.safe_load(f)
    log_filepath = join(expanduser('~'), 'logs', 'liker')
    log_filepath += datetime.now().strftime('/%y/%m/%d/%H_%M_%S%f.log')
    log_dir = dirname(log_filepath)
    makedirs(log_dir, exist_ok=True)
    log_conf['handlers']['h_file']['filename'] = log_filepath
    dictConfig(log_conf)


def get_cred_file():
    from os.path import dirname, join
    module_file = dirname(__file__)
    credentials_file = join(module_file, 'credentials.yaml')
    return credentials_file


init_logging()
credentials_file = get_cred_file()
