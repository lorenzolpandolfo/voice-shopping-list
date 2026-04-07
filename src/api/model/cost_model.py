from dataclasses import dataclass
from datetime import datetime


@dataclass
class Cost:
    id: int | None
    title: str
    dates: list[datetime]
