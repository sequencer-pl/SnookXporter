from unittest import TestCase
from unittest.mock import mock_open, patch

from settings.config import ConfigParser
from snookxporter.clients.snookapp import SnookAppConfig
from snookxporter.entities import Player

CONFIG_YAML_CONTENT = """
snook_app:
  base_url: http://snook.app
  bookings_endpoint: /endpoint
  
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

    def test_get_players_returns_list_of_player_objects(self, m_open):
        expected_players = [
            Player(first_name="Player", last_name="One", alias="p1"),
            Player(first_name="Player", last_name="Two"),
        ]

        players = ConfigParser().get_players()

        m_open.assert_called_once()
        self.assertListEqual(expected_players, players)
