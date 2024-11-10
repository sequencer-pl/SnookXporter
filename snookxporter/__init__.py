import logging
import os

from settings.config import ConfigParser

config_parser = ConfigParser()

logging.basicConfig(
    level=logging.DEBUG,
    format= '[%(asctime)s (%(filename)s:%(lineno)d) %(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(config_parser.get_root_dir(), "logs/debug.log")),
        logging.StreamHandler(),
    ]
 )
