from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from google.oauth2.credentials import Credentials

from snookxporter.clients.google.calendar import GoogleCalendarClient, GoogleCalendarConfig
from snookxporter.clients.google.formats import GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE
from snookxporter.entities import Match, Player


class GoogleCalendarTest(TestCase):
    def setUp(self):
        self.token = {
            "token": "token",
            "refresh_token": "refresh_token",
            "token_uri": "token_uri",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scopes": "scopes",
            "expiry": "2000-01-01T10:00:00.12345Z",
        }
        self.config = GoogleCalendarConfig(
            id="id@google.com",
            players=[
                Player(first_name="Player", last_name="One"),
                Player(first_name="Player", last_name="Two", alias='P2'),
            ]
        )
        self.client = GoogleCalendarClient(config=self.config, token=self.token)
        self.calendar_items = {
            "items": [
                {
                    'id': 'item_id_1',
                    'summary': 'Marty McFly 2:3 Emmet Brown',
                    'description': 'Marty McFly 2:3 Emmet Brown\nTable number 1',
                    'start': {'dateTime': '2024-11-05T21:00:00+01:00', 'timeZone': 'Europe/Warsaw'},
                    'end': {'dateTime': '2024-11-05T23:00:00+01:00', 'timeZone': 'Europe/Warsaw'},
                }, {
                    'id': 'item_id_2',
                    'summary': 'Emmet Brown v Marty McFly',
                    'description': 'Emmet Brown v Marty McFly\nTable number 5',
                    'start': {'dateTime': '2024-11-06T21:00:00+01:00', 'timeZone': 'Europe/Warsaw'},
                    'end': {'dateTime': '2024-11-06T23:00:00+01:00', 'timeZone': 'Europe/Warsaw'},
                }, {
                    'id': 'invalid_item_id_3',
                    'summary': 'Invalid Summary',
                    'description': 'Invalid Description',
                    'start': {'dateTime': '2024-11-07T21:00:00+01:00', 'timeZone': 'Europe/Warsaw'},
                    'end': {'dateTime': '2024-11-07T23:00:00+01:00', 'timeZone': 'Europe/Warsaw'},
                }
            ]
        }

    def test_get_credentials_from_token_json_returns_credentials_instance(self):
        client = GoogleCalendarClient(
            config=self.config,
            token=self.token
        )

        self.assertIsInstance(client.credentials, Credentials)

    @patch("snookxporter.clients.google.calendar.os")
    @patch("snookxporter.clients.google.calendar.Credentials")
    def test_get_credentials_returns_credentials_instance_if_token_exists(self, m_credentials, m_os):
        credentials = MagicMock()
        credentials.valid = True
        m_os.path.exists.return_value = True
        m_credentials.from_authorized_user_file.return_value = expected_credentials = credentials

        client = GoogleCalendarClient(config=self.config)

        self.assertEqual(expected_credentials, client.credentials)

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("snookxporter.clients.google.calendar.os")
    @patch("snookxporter.clients.google.calendar.Credentials")
    def test_get_credentials_returns_credentials_instance_if_invalid_expired_credentials(
            self, m_credentials, m_os, m_open
    ):
        credentials = MagicMock()
        credentials.valid = False
        credentials.expired = True
        credentials.refresh_token = True
        m_os.path.exists.return_value = True
        m_credentials.from_authorized_user_file.return_value = expected_credentials = credentials
        expected_credentials.to_json.return_value = credentials_json = "json"

        client = GoogleCalendarClient(config=self.config)

        credentials.refresh.assert_called_once()
        m_open.return_value.write.assert_called_once_with(credentials_json)
        self.assertEqual(expected_credentials, client.credentials)

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("snookxporter.clients.google.calendar.InstalledAppFlow")
    @patch("snookxporter.clients.google.calendar.os")
    @patch("snookxporter.clients.google.calendar.Credentials")
    def test_get_credentials_returns_credentials_instance_if_invalid_credentials(
            self, m_credentials, m_os, m_installed_app_flow, m_open
    ):
        credentials = MagicMock()
        credentials.valid = False
        credentials.expired = False
        credentials.refresh_token = False
        m_os.path.exists.return_value = True
        m_credentials.from_authorized_user_file.return_value = expected_credentials = credentials
        expected_credentials.to_json.return_value = credentials_json = "json"
        m_installed_app_flow.from_client_secrets_file.return_value = m_flow = MagicMock()
        m_flow.run_local_server.return_value = expected_credentials


        client = GoogleCalendarClient(config=self.config)

        m_installed_app_flow.from_client_secrets_file.assert_called_once()
        m_open.return_value.write.assert_called_once_with(credentials_json)
        self.assertEqual(expected_credentials, client.credentials)

    @patch("snookxporter.clients.google.calendar.build")
    def test_get_events_returns_list_of_valid_match_objects(self, m_build):
        past_days = 3
        future_days = 26
        m_build.return_value.events.return_value.list.return_value.execute.return_value = self.calendar_items
        item1, item2 = self.calendar_items["items"][0], self.calendar_items["items"][1]
        expected_matches = [
            Match(
                item_id=item1["id"],
                host=Player(first_name="Marty", last_name="McFly"),
                guest=Player(first_name="Emmet", last_name="Brown"),
                start=datetime.strptime(item1["start"]["dateTime"], GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                end=datetime.strptime(item1["end"]["dateTime"], GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                host_score=2,
                guest_score=3,
                table=1,
            ),
            Match(
                item_id=item2["id"],
                host=Player(first_name="Emmet", last_name="Brown"),
                guest=Player(first_name="Marty", last_name="McFly"),
                start=datetime.strptime(item2["start"]["dateTime"], GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                end=datetime.strptime(item2["end"]["dateTime"], GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                table=5,
            ),
            Match.get_match_to_delete_from_calendar(item_id='invalid_item_id_3'),
        ]

        matches = self.client.get_events(past_days=past_days, future_days=future_days)

        self.assertListEqual(expected_matches, matches)

    @patch("snookxporter.clients.google.calendar.build")
    def test_add_events_executes_insert_to_calendar(self, m_build):
        matches = {
            Match(
                host=Player(first_name="Marty", last_name="McFly"),
                guest=Player(first_name="Emmet", last_name="Brown"),
                start=datetime(2024, 11, 5, 21, 30),
                end=datetime(2024, 11, 5, 23, 00),
                host_score=2,
                guest_score=3,
                table=1,
            )
        }
        m_insert = m_build.return_value.events.return_value.insert

        self.client.add_events(schedule=matches)

        m_insert.assert_called_once_with(
            calendarId="id@google.com", body={
                "summary": "Marty McFly 2:3 Emmet Brown",
                "description": "Marty McFly 2:3 Emmet Brown\nTable number 1\n",
                "start": {
                    "dateTime": "2024-11-05T21:30:00",
                    "timeZone": "Europe/Warsaw"
                },
                "end": {
                    "dateTime": "2024-11-05T23:00:00",
                    "timeZone": "Europe/Warsaw"
                }
            }
        )
        m_insert.return_value.execute.assert_called_once()

    @patch("snookxporter.clients.google.calendar.build")
    def test_delete_events_executes_delete_to_calendar(self, m_build):
        expected_item_id = "item_id_1"
        matches = {
            Match(
                item_id=expected_item_id,
                host=Player(first_name="Dummy", last_name="Player"),
                guest=Player(first_name="Dummy", last_name="Player"),
                start=datetime(2024, 11, 5, 21, 30),
                end=datetime(2024, 11, 5, 23, 00),
            )
        }
        m_delete = m_build.return_value.events.return_value.delete

        self.client.delete_events(schedule=matches)


        m_delete.assert_called_once_with(
            calendarId="id@google.com", eventId=expected_item_id
        )
        m_delete.return_value.execute.assert_called_once()
