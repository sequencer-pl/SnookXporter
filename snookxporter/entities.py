from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Player:
    first_name: str
    last_name: str
    alias: str | None = None

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

    def __eq__(self, other):
        return self.first_name == other.first_name and self.last_name == other.last_name

    def __hash__(self):
        return hash((self.first_name, self.last_name))

@dataclass(frozen=True)
class Match:
    host: Player
    guest: Player
    start: datetime
    end: datetime
    host_score: int | None = None
    guest_score: int | None = None
    item_id: str | None = None
    table: int | None = None

    def __eq__(self, other):
        return (self.host == other.host and self.guest == other.guest
                and self.start == other.start and self.end == other.end
                and self.host_score == other.host_score and self.guest_score == other.guest_score)

    def __hash__(self):
        return hash(
            (self.host, self.guest, self.start, self.end,
             self.host_score, self.guest_score, self.table)
        )

    def get_match_calendar_summary(self):
        host = self.host.alias if self.host.alias else self.host
        guest = self.guest.alias if self.guest.alias else self.guest
        reverse = self.guest.alias and not self.host.alias
        return f"{host} {self._get_vs_or_score()} {guest}" \
            if not reverse \
            else f"{guest} {"".join(reversed(self._get_vs_or_score()))} {host}"

    def get_match_calendar_description(self):
        return (f"{self.host} {self._get_vs_or_score()} {self.guest}\n"
                f"Table number {self.table}\n")


    def __post_init__(self):
        if self.start.tzinfo:
            object.__setattr__(self, 'start', self.start.replace(tzinfo=None))
        if self.end.tzinfo:
            object.__setattr__(self, 'end', self.end.replace(tzinfo=None))

    def _is_finished(self):
        return self.host_score and self.guest_score

    def _get_vs_or_score(self):
        return f"{self.host_score}:{self.guest_score}" if self._is_finished() else "v"

    @classmethod
    def get_match_to_delete_from_calendar(cls, item_id: str) -> 'Match':
        dummy_player = Player(
            first_name="Dummy",
            last_name="Player",
        )
        return Match(
            host=dummy_player,
            guest=dummy_player,
            start=datetime.fromtimestamp(0),
            end=datetime.fromtimestamp(0),
            item_id=item_id,
        )
