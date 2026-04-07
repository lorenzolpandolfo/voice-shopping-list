from dataclasses import dataclass


@dataclass
class User:
    id: str
    token: str
    spreadsheet_id: str
    spreadsheet_tab: str
