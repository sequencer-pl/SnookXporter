from datetime import datetime, timezone
from unittest import TestCase

from parameterized import parameterized

from snookxporter.entities import Match, Player


class PlayerTest(TestCase):

    def test_player_repr(self):

        p1 = Player(first_name="Player", last_name="One", alias="P1")
        p2 = Player(first_name="Player", last_name="Two")

        self.assertEqual(repr(p1), "Player One")
        self.assertEqual(repr(p2), "Player Two")

    def test_players_compare(self):

        p1 = Player(first_name="The Same", last_name="Player", alias="P1")
        p2 = Player(first_name="The Same", last_name="Player", alias="P2")
        p3 = Player(first_name="The Same", last_name="Player")

        self.assertEqual(p1, p2)
        self.assertEqual(p1, p3)
        self.assertEqual(p2, p3)


class MatchTest(TestCase):
    def setUp(self):
        self.datetime_format = "%Y-%m-%d %H:%M:%S"
        self.match_scheduled = Match(
            host=Player(
                first_name="Player",
                last_name="One",
            ),
            guest=Player(
                first_name="Player",
                last_name="Two"
            ),
            start=datetime.strptime("2024-12-01 12:00:00",self.datetime_format),
            end=datetime.strptime("2024-12-01 15:00:00", self.datetime_format),
            table=1,
        )
        self.match_finished = Match(
            host=Player(
                first_name="Player",
                last_name="One",
            ),
            guest=Player(
                first_name="Player",
                last_name="Two",
        ),
            start=datetime.strptime("2024-11-03 18:00:00",self.datetime_format),
            end=datetime.strptime("2024-11-03 21:00:00", self.datetime_format),
            host_score=2,
            guest_score=3,
            table=2,
        )

    def test_matches_equality(self):
        match_with_item_id = Match(
            host=Player(
                first_name="Player",
                last_name="One",
            ),
            guest=Player(
                first_name="Player",
                last_name="Two"
            ),
            start=datetime.strptime("2024-12-01 12:00:00",self.datetime_format),
            end=datetime.strptime("2024-12-01 15:00:00", self.datetime_format),
            host_score=2,
            guest_score=3,
            table=1,
            item_id="123"
        )
        match_without_item_id = Match(
            host=Player(
                first_name="Player",
                last_name="One",
            ),
            guest=Player(
                first_name="Player",
                last_name="Two"
            ),
            start=datetime.strptime("2024-12-01 12:00:00",self.datetime_format),
            end=datetime.strptime("2024-12-01 15:00:00", self.datetime_format),
            host_score=2,
            guest_score=3,
            table=1,
        )

        self.assertEqual(match_with_item_id, match_without_item_id)
        self.assertSetEqual(set(), {match_with_item_id} - {match_without_item_id})

    @parameterized.expand([
        (None, None, None, None, "Player One v Player Two"),
        ("P1", None, None, None, "P1 v Player Two"),
        (None, "P2", None, None, "P2 v Player One"),
        ("P1", "P2", None, None, "P1 v P2"),
        (None, None, 3, 2, "Player One 3:2 Player Two"),
        ("P1", None, 3, 2, "P1 3:2 Player Two"),
        (None, "P2", 3, 2, "P2 2:3 Player One"),
        ("P1", "P2", 3, 2, "P1 3:2 P2"),
    ])
    def test_get_match_calendar_summary(
            self, p1_alias, p2_alias, host_score, guest_score, expected_match_summary
    ):
        player1 = "Player One"
        player2 = "Player Two"
        match = Match(
            host=Player(
                first_name=player1.split(" ")[0],
                last_name=player1.split(" ")[1],
                alias=p1_alias,
            ),
            guest=Player(
                first_name=player2.split(" ")[0],
                last_name=player2.split(" ")[1],
                alias=p2_alias,
        ),
            start=datetime.strptime("2024-11-03 18:00:00",self.datetime_format),
            end=datetime.strptime("2024-11-03 21:00:00", self.datetime_format),
            host_score=host_score,
            guest_score=guest_score,
        )

        match_summary = match.get_match_calendar_summary()

        self.assertEqual(expected_match_summary, match_summary)

    def test_match_calendar_description_returns_full_desc(self):
        expected_scheduled_match_description = (
            "Player One v Player Two\n"
            "Table number 1\n"
        )
        expected_finished_match_description = (
            "Player One 2:3 Player Two\n"
            "Table number 2\n"
        )

        self.assertEqual(
            expected_scheduled_match_description,
            self.match_scheduled.get_match_calendar_description()
        )
        self.assertEqual(
            expected_finished_match_description,
            self.match_finished.get_match_calendar_description()
        )

    def test_match_to_delete_from_calendar_returns_dummy_match_with_item_id(self):
        to_delete_item_id = "to_delete_item_id"
        dummy_player = Player(
            first_name="Dummy",
            last_name="Player",
        )
        expected_dummy_match = Match(
            host=dummy_player,
            guest=dummy_player,
            start=datetime.fromtimestamp(0),
            end=datetime.fromtimestamp(0),
            item_id=to_delete_item_id
        )

        dummy_match = Match.get_match_to_delete_from_calendar(item_id=to_delete_item_id)

        self.assertEqual(expected_dummy_match, dummy_match)

    def test_match_post_init_removes_timezone_info_from_datetime_objects(self):
        fixed_now = datetime.now(tz=timezone.utc)

        m1 = Match(
            host=(Player(
                first_name="Player",
                last_name="One",
            )),
            guest=(Player(
                first_name="Player",
                last_name="Two",
            )),
            start=fixed_now,
            end=fixed_now,
        )

        self.assertIsNone(m1.start.tzinfo)
        self.assertIsNone(m1.end.tzinfo)
