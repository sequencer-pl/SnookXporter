from datetime import datetime, timedelta

import requests

from snookxporter.dataclasses import Match, User


class SnookAppClient:
    def __init__(self, base_url: str, endpoint: str):
        self.base_url = base_url
        self.endpoint = endpoint
        self.date_format = "%Y-%m-%d"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

    def get_arriving_matches_for(self, users: list[User]) -> list[Match]:
        matches = self._get_schedule()
        return self._fetch_important_matches(matches, users)

    def _fetch_important_matches(self, matches, users) -> list[Match]:
        return [
            Match(
                host=User(
                    firstName=item['match']['host']['firstName'],
                    lastName=item['match']['host']['lastName'],
                ),
                guest=User(
                    firstName=item['match']['guest']['firstName'],
                    lastName=item['match']['guest']['lastName'],
                ),
                start=datetime.strptime(f"{match['date']} {item['timeFrom']}", self.datetime_format),
                end=datetime.strptime(f"{match['date']} {item['timeTo']}", self.datetime_format),
                host_score=item['match']['matchResult']['gamesHost'] if item['match'].get('matchResult') else None,
                guest_score=item['match']['matchResult']['gamesGuest'] if item['match'].get('matchResult') else None,
            )
            for match in matches
            for court in match['matchCourts']
            for item in court['bookingItems']
            if item.get('match') and self._is_host_or_guest_in_users(
                host=item['match']['host'],
                guest=item['match']['guest'],
                users=users
            )
        ]

    def _get_schedule(self) -> list[dict]:
        _from = (datetime.today() - timedelta(days=1)).strftime(self.date_format)
        _to = (datetime.today() + timedelta(days=14)).strftime(self.date_format)
        url = f"{self.base_url}{self.endpoint}?from={_from}&to={_to}"
        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()['bookings']['days']['SNOOKER']

    @staticmethod
    def _is_host_or_guest_in_users(host: dict, guest: dict, users: list[User]):
        return User(
            firstName=host['firstName'],
            lastName=host['lastName'],
        ) in users or User(
            firstName=guest['firstName'],
            lastName=guest['lastName'],
        ) in users
