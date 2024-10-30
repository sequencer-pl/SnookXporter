from datetime import datetime
from unittest import TestCase

import responses
from freezegun import freeze_time

from snookxporter.clients.snookapp import SnookAppClient
from snookxporter.dataclasses import Match, User


class SnookAppTest(TestCase):
    def setUp(self):
        self.base_url = "http://snook.app.url"
        self.endpoint = "/api"
        self.client = SnookAppClient(base_url=self.base_url, endpoint=self.endpoint)

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

    @responses.activate
    @freeze_time('1955-11-05')
    def test_get_arriving_matches_returns_list_of_users_games(self):
        url = f"{self.base_url}{self.endpoint}?from=1955-11-04&to=1955-11-19"
        responses.add(responses.GET, url, json=self.sample_response, status=200)
        users = [
            User(firstName='Marty', lastName='McFly'),
            User(firstName='Emmet', lastName='Brown'),
        ]
        expected_matches = [
            Match(
                host=User(firstName='Marty', lastName='McFly'),
                guest=User(firstName='Emmet', lastName='Brown'),
                start=datetime(year=1955, month=11, day=4, hour=6, minute=30),
                end=datetime(year=1955, month=11, day=4, hour=7, minute=30),
                host_score=3,
                guest_score=2,
            ),
            Match(
                host=User(firstName='Marty', lastName='McFly'),
                guest=User(firstName='Biff', lastName='Tannen'),
                start=datetime(year=1955, month=11, day=5, hour=16, minute=30),
                end=datetime(year=1955, month=11, day=5, hour=20, minute=0),
                host_score=None,
                guest_score=None,
            ),
        ]

        matches = self.client.get_arriving_matches_for(users=users)

        self.assertListEqual(expected_matches, matches)
