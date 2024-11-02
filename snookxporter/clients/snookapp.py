from dataclasses import dataclass
from datetime import datetime, timedelta

import requests

from snookxporter.entities import Match, Player


@dataclass
class SnookAppConfig:
    base_url: str
    bookings_endpoint: str

    def __post_init__(self):
        self.url = f"{self.base_url}{self.bookings_endpoint}"


class SnookAppClient:
    def __init__(self, config: SnookAppConfig):
        self.config = config
        self.date_format = "%Y-%m-%d"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

    def extract_players_matches_from_schedule(self, schedule: list[dict], players: list[Player]) -> list[Match]:
        return [
            Match(
                host=Player(
                    first_name=item['match']['host']['firstName'],
                    last_name=item['match']['host']['lastName'],
                    alias=self._get_alias_for_player(item['match']['host'], players=players),
                ),
                guest=Player(
                    first_name=item['match']['guest']['firstName'],
                    last_name=item['match']['guest']['lastName'],
                    alias=self._get_alias_for_player(item['match']['guest'], players=players),
                ),
                start=datetime.strptime(f"{match['date']} {item['timeFrom']}", self.datetime_format),
                end=datetime.strptime(f"{match['date']} {item['timeTo']}", self.datetime_format),
                host_score=item['match']['matchResult']['gamesHost'] if item['match'].get('matchResult') else None,
                guest_score=item['match']['matchResult']['gamesGuest'] if item['match'].get('matchResult') else None,
                table=court['number']
            )
            for match in schedule
            for court in match['matchCourts']
            for item in court['bookingItems']
            if item.get('match') and self._is_host_or_guest_in_players(
                host=item['match']['host'],
                guest=item['match']['guest'],
                players=players
            )
        ]

    def get_schedule(self, past_days: int, future_days: int) -> list[dict]:
        _from = (datetime.today() - timedelta(days=past_days)).strftime(self.date_format)
        _to = (datetime.today() + timedelta(days=future_days)).strftime(self.date_format)
        url = f"{self.config.url}?from={_from}&to={_to}"
        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()['bookings']['days']['SNOOKER']

    @staticmethod
    def _is_host_or_guest_in_players(host: dict, guest: dict, players: list[Player]):
        return Player(
            first_name=host['firstName'],
            last_name=host['lastName'],
        ) in players or Player(
            first_name=guest['firstName'],
            last_name=guest['lastName'],
        ) in players

    @staticmethod
    def _get_alias_for_player(player: dict, players: list[Player]):
        alias = [p.alias for p in players
                 if p.first_name == player['firstName']
                 and p.last_name == player['lastName']]
        return alias[0] if alias else None
