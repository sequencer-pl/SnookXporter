from datetime import datetime
from unittest import TestCase

import responses
from freezegun import freeze_time

from snookxporter.clients.snookapp import SnookAppClient, SnookAppConfig
from snookxporter.entities import Match, Player


class SnookAppClientTest(TestCase):
    def setUp(self):
        self.config = SnookAppConfig(
            base_url="http://snook.app.url",
            bookings_endpoint="/api"
        )
        self.client = SnookAppClient(config=self.config)

        self.sample_response = {
            "bookings": {
                "days": {
                    "SNOOKER": [
                        {
                            "date": "1955-11-04",
                            "matchCourts": [
                                {
                                    "type": "SNOOKER_TABLE",
                                    "number": 1,
                                    "bookingItems": [
                                        {
                                            "timeFrom": "06:30:00",
                                            "timeTo": "07:30:00",
                                            "match": {
                                                "host": {
                                                    "firstName": "Marty",
                                                    "lastName": "McFly",
                                                },
                                                "guest": {
                                                    "firstName": "Emmet",
                                                    "lastName": "Brown",
                                                },
                                                "matchResult": {
                                                    "gamesHost": 3,
                                                    "gamesGuest": 2,
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "date": "1955-11-05",
                            "matchCourts": [
                                {
                                    "type": "SNOOKER_TABLE",
                                    "number": 1,
                                    "bookingItems": [
                                        {
                                            "timeFrom": "16:30:00",
                                            "timeTo": "20:00:00",
                                            "match": {
                                                "host": {
                                                    "firstName": "Marty",
                                                    "lastName": "McFly",
                                                },
                                                "guest": {
                                                    "firstName": "Biff",
                                                    "lastName": "Tannen",
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "date": "1955-11-15",
                            "matchCourts": [
                                {
                                    "type": "SNOOKER_TABLE",
                                    "number": 1,
                                    "bookingItems": [
                                        {
                                            "timeFrom": "08:30:00",
                                            "timeTo": "10:00:00",
                                            "match": {
                                                "host": {
                                                    "firstName": "George",
                                                    "lastName": "McFly",
                                                },
                                                "guest": {
                                                    "firstName": "Mr",
                                                    "lastName": "Strickland",
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }


    def test_extract_players_matches_from_schedule_returns_only_players_related_matches(self):
        players = [
            Player(first_name="Marty", last_name="McFly"),
            Player(first_name="Emmet", last_name="Brown"),
        ]
        biff_tannen = Player(first_name="Biff", last_name="Tannen")
        expected_matches = [
            Match(
                host=players[0],
                guest=players[1],
                start=datetime(1955, 11, 4, 6, 30),
                end=datetime(1955, 11, 4, 7, 30),
                host_score=3,
                guest_score=2,
                table=1,
            ),
            Match(
                host=players[0],
                guest=biff_tannen,
                start=datetime(1955, 11, 5, 16, 30),
                end=datetime(1955, 11, 5, 20, 0),
                host_score=None,
                guest_score=None,
            )
        ]

        matches = self.client.extract_players_matches_from_schedule(
            players=players,
            schedule=self.sample_response["bookings"]["days"]["SNOOKER"]
        )

        self.assertListEqual(expected_matches, matches)

    @responses.activate
    @freeze_time("1955-11-05")
    def test_get_schedule_does_request_and_returns_schedule_only(self):
        responses.get(
            url=f"{self.config.url}?from=1955-11-02&to=1955-11-11",
            json=self.sample_response,
            status=200
        )

        schedule = self.client.get_schedule(
            past_days=3,
            future_days=6
        )

        self.assertListEqual(self.sample_response["bookings"]["days"]["SNOOKER"], schedule)
