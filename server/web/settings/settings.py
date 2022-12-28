import pathlib
import yaml
import logging


BASE_DIR = pathlib.Path(__file__).parent.parent.parent
config_path = BASE_DIR / 'web' / 'settings' / 'config.yaml'


def get_config(path):
    with open(path) as file:
        config = yaml.safe_load(file)
    return config


config = get_config(config_path)

logging.basicConfig(level=logging.DEBUG, filename=BASE_DIR / config['log_path'], filemode='w')
