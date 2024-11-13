import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from snookxporter.clients.google.formats import (GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE,
                                                 GOOGLE_CALENDAR_DATETIME_FORMAT_WITHOUT_TIMEZONE,
                                                 GOOGLE_CALENDAR_DATETIME_TOKEN_JSON_FORMAT)
from snookxporter.entities import Match, Player

logger = logging.getLogger(__name__)


TOKEN_PATH = 'secrets/token.json'
CREDENTIALS_PATH = 'secrets/credentials.json'


@dataclass
class GoogleCalendarConfig:
    id: str
    players: list[Player]


class GoogleCalendarClient:
    def __init__(self, config=GoogleCalendarConfig, token: dict | None = None):
        self.token = token
        self.calendar_id = config.id
        self.players = config.players
        self.scopes = ["https://www.googleapis.com/auth/calendar.events"]
        self.credentials = self._get_credentials_from_token_json()

    def get_events(self, past_days: int, future_days: int) -> list[Match]:
        service = build('calendar', 'v3', credentials=self.credentials)
        _from = (datetime.today() - timedelta(days=past_days)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        _to = (_from + timedelta(days=future_days)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        logger.info(f'Getting calendar {self.calendar_id} events from {_from} to {_to}')
        events_result = service.events().list(  # pylint: disable=maybe-no-member
            calendarId=self.calendar_id,
            timeMin=_from.strftime(GOOGLE_CALENDAR_DATETIME_FORMAT_WITHOUT_TIMEZONE),
            timeMax=_to.strftime(GOOGLE_CALENDAR_DATETIME_FORMAT_WITHOUT_TIMEZONE),
            maxResults=99_999,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        matches = []
        for item in events_result['items']:
            try:
                matches.append(Match(
                    host=Player(**self._parse_description(item['description'])['host']),
                    guest=Player(**self._parse_description(item['description'])['guest']),
                    start=datetime.strptime(item['start']['dateTime'], GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                    end=datetime.strptime(item['end']['dateTime'], GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                    item_id=item['id'],
                    host_score=self._parse_description(item['description'])['host_score'],
                    guest_score=self._parse_description(item['description'])['guest_score'],
                    table=self._parse_description(item['description'])['table']
                ))
            except (IndexError, ValueError) as e:
                logger.warning(f"Problem with parsing calendar item: {item}: Error: {e}")
                matches.append(Match.get_match_to_delete_from_calendar(item['id']))
        return matches

    def add_events(self, schedule: set[Match]) -> None:
        service = build('calendar', 'v3', credentials=self.credentials)
        for match in schedule:
            event = {
                'summary': match.get_match_calendar_summary(),
                'description': match.get_match_calendar_description(),
                'start': {
                    'dateTime': match.start.strftime(GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                    'timeZone': 'Europe/Warsaw'
                },
                'end': {
                    'dateTime': match.end.strftime(GOOGLE_CALENDAR_DATETIME_FORMAT_WITH_TIMEZONE),
                    'timeZone': 'Europe/Warsaw'
                }
            }
            service.events().insert(calendarId=self.calendar_id, body=event).execute()  # pylint: disable=maybe-no-member

    def delete_events(self, schedule: set[Match]) -> None:
        service = build('calendar', 'v3', credentials=self.credentials)
        for match in schedule:
            service.events().delete(  # pylint: disable=maybe-no-member
                calendarId=self.calendar_id, eventId=match.item_id
            ).execute()

    @staticmethod
    def _parse_description(description: str) -> dict:
        lines = description.split("\n")
        return {
            'host': {
                'first_name': lines[0].split(" ")[0],
                'last_name': lines[0].split(" ")[1],
            },
            'guest': {
                'first_name': lines[0].split(" ")[-2],
                'last_name': lines[0].split(" ")[-1],
            },
            'host_score': int(lines[0].split(" ")[2].split(":")[0]) if ":" in lines[0] else None,
            'guest_score': int(lines[0].split(" ")[2].split(":")[1]) if ":" in lines[0] else None,
            'table': int(lines[1].split(" ")[2]),
        }

    def _get_credentials_from_token_json(self) -> Credentials:
        if not self.token:
            return self._get_credentials()
        else:
            return Credentials(
                token=self.token['token'],
                refresh_token=self.token['refresh_token'],
                token_uri=self.token['token_uri'],
                client_id=self.token['client_id'],
                client_secret=self.token['client_secret'],
                scopes=self.token['scopes'],
                expiry=datetime.strptime(self.token['expiry'], GOOGLE_CALENDAR_DATETIME_TOKEN_JSON_FORMAT)
            )


    def _get_credentials(self) -> Credentials:
        """
        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        If there are no (valid) credentials available, let the user log in.

        At the end save the credentials for the next run and return user credentials
        """
        credentials = None
        if os.path.exists(TOKEN_PATH):
            credentials = Credentials.from_authorized_user_file(TOKEN_PATH, self.scopes)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, self.scopes)
                credentials = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w', encoding='utf8') as token:
                token.write(credentials.to_json())
        return credentials
