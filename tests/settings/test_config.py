from pathlib import Path
from unittest import TestCase
from unittest.mock import mock_open, patch

from snookxporter.clients.google.calendar import GoogleCalendarConfig
from snookxporter.clients.snookapp import SnookAppConfig
from snookxporter.entities import Player
from snookxporter.settings.config import ConfigParser

CONFIG_YAML_CONTENT = """
snook_app:
  base_url: http://snook.app
  bookings_endpoint: /endpoint

calendars:
  - id: id1
    players:
      - first_name: Player
        last_name: One
        alias: p1
      - first_name: Player
        last_name: Two
"""


@patch("builtins.open", new_callable=mock_open, read_data=CONFIG_YAML_CONTENT)
class ConfigTest(TestCase):

    def test_get_snook_app_config_returns_config_object(self, m_open):
        expected_config = SnookAppConfig(
            base_url="http://snook.app",
            bookings_endpoint="/endpoint",
        )

        config = ConfigParser().get_snook_app_config()

        m_open.assert_called_once()
        self.assertEqual(expected_config, config)

    def test_get_calendar_config_returns_proper_object(self, m_open):
        config_parser = ConfigParser()
        expected_calendars_config = [
            GoogleCalendarConfig(
                id="id1",
                players=[
                    Player(first_name="Player", last_name="One", alias="p1"),
                    Player(first_name="Player", last_name="Two"),
                ]
            )
        ]

        calendar_config = config_parser.get_calendars_config()

        m_open.assert_called_once()
        self.assertListEqual(expected_calendars_config, calendar_config)

    def test_get_root_dir_raises_runtime_error(self, _):
        fake_start = Path("wrong_file_name.py")

        with (
            patch("snookxporter.settings.config.__file__", str(fake_start)),
            patch("pathlib.Path.resolve", return_value=fake_start)
        ):
            with self.assertRaises(RuntimeError):
                ConfigParser.get_root_dir()
