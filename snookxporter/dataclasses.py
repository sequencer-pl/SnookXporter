from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    firstName: str
    lastName: str


@dataclass
class Match:
    host: User
    guest: User
    start: datetime
    end: datetime
    host_score: int | None = None
    guest_score: int | None = None
