import json
import logging
from datetime import datetime

import click

from settings.config import ConfigParser
from snookxporter.clients.google.calendar import GoogleCalendarClient
from snookxporter.clients.snookapp import SnookAppClient
from snookxporter.entities import Match, Player

logger = logging.getLogger(__name__)


@click.command()
@click.option('--past-days',
              help="Number of past days to synchronize.",
              default=1, type=int)
@click.option('--future-days',
              help="Number of future days to synchronize.",
              default=90, type=int)
@click.option('--token',
              help="Google Calendar token.",
              default = '{}')
def run(past_days, future_days, token) -> None:

    config_parser = ConfigParser()
    snook_app_config = config_parser.get_snook_app_config()
    calendars_config = config_parser.get_calendars_config()
    token = json.loads(token)

    snook_app_client = SnookAppClient(config=snook_app_config)
    decider_schedule = snook_app_client.get_schedule(past_days=past_days, future_days=future_days)

    for calendar in calendars_config:
        calendar_client = GoogleCalendarClient(config=calendar, token=token)

        calendar_events = calendar_client.get_events(past_days=past_days, future_days=future_days)
        logger.debug(f"Calendar events: {calendar_events}")

        decider_matches = snook_app_client.extract_players_matches_from_schedule(
            schedule=decider_schedule, players=calendar.players
        )
        logger.debug(f"Decider matches: {decider_matches}")

        to_add = set(decider_matches) - set(calendar_events)
        logger.info(f"Events to add to calendar ({calendar_client.calendar_id}): {to_add}")
        calendar_client.add_events(to_add)

        to_remove = set(calendar_events) - set(decider_matches)
        logger.info(f"Events to remove from calendar ({calendar_client.calendar_id}): {to_remove}")
        calendar_client.delete_events(to_remove)
