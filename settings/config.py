import logging
import os
from pathlib import Path

import yaml

from snookxporter.clients.google.calendar import GoogleCalendarConfig
from snookxporter.clients.snookapp import SnookAppConfig
from snookxporter.entities import Player

ROOT_DIR = "SnookXporter"

logger = logging.getLogger(__name__)


class ConfigParser:
    def __init__(self):
        root_dir = self.get_root_dir()
        self.config_path = os.path.join(root_dir, 'settings/config.yaml')
        self.config = self._get_config()
        logger.debug(f"Using config: {self.config}")

    def get_snook_app_config(self) -> SnookAppConfig:
        return SnookAppConfig(**self.config['snook_app'])

    def get_calendars_config(self) -> list[GoogleCalendarConfig]:
        return [
            GoogleCalendarConfig(
                id=cal['id'],
                players=[ Player(**player) for player in cal['players'] ]
            ) for cal in self.config['calendars']
        ]

    def get_players(self):
        return [Player(**p) for p in self.config['players']]

    @staticmethod
    def get_root_dir():
        path = Path(__file__).resolve()
        while path.name != ROOT_DIR:
            path = path.parent
            if path == path.parent:
                raise RuntimeError(f"There is no directory {ROOT_DIR} in project")
        return path

    def _get_config(self):
        with open(self.config_path) as config_file:
            return yaml.safe_load(config_file)
