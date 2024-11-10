from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from click.testing import CliRunner

from snookxporter.__main__ import run
from snookxporter.clients.google.calendar import GoogleCalendarConfig


class MainTest(TestCase):

    @patch('snookxporter.__main__.GoogleCalendarClient')
    @patch('snookxporter.__main__.SnookAppClient')
    @patch('snookxporter.__main__.ConfigParser')
    def test_run_executes_all_necessary_methods_with_args(
            self, m_config_parser, m_snook_app_client_class, m_google_calendar_client_class,
    ):
        m_config_parser.return_value.get_calendars_config.return_value = [
            GoogleCalendarConfig(id="11", players=[]),
            GoogleCalendarConfig(id="22", players=[]),
        ]
        m_snook_app_client_class.return_value = m_snook_app_client = MagicMock()
        m_first_calendar_client, m_second_calendar_client = MagicMock(), MagicMock()
        m_google_calendar_client_class.side_effect = [
            m_first_calendar_client, m_second_calendar_client
        ]
        runner = CliRunner()

        runner.invoke(run, ["--past-days", "1", "--future-days", "2"])

        m_snook_app_client.get_schedule.assert_called_once_with(
            past_days=1, future_days=2
        )
        m_google_calendar_client_class.assert_has_calls([
            call(config=GoogleCalendarConfig(id="11", players=[]), token={}),
            call(config=GoogleCalendarConfig(id="22", players=[]), token={})
        ])
        m_first_calendar_client.get_events.assert_called_once_with(past_days=1, future_days=2)
        m_second_calendar_client.get_events.assert_called_once_with(past_days=1, future_days=2)
        self.assertEqual(2, m_snook_app_client.extract_players_matches_from_schedule.call_count)
