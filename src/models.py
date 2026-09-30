from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Expense:
    amount_paise: int          # money stored as integer paise, not float
    description: str
    spent_on: date
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    id: Optional[int] = None