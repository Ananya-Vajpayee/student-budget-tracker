import sqlite3
import logging
from contextlib import contextmanager
from datetime import date

from exceptions import ValidationError, NotFoundError, DatabaseError
from models import Expense

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    amount_paise INTEGER NOT NULL CHECK (amount_paise > 0),
    description TEXT NOT NULL,
    spent_on TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    group_id INTEGER
);
"""


class Database:
    def __init__(self, path="budget.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    @contextmanager
    def transaction(self):
        """Commit on success, roll back on any error (reliability NFR)."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            log.exception("Transaction rolled back")
            raise

    def add_expense(self, exp: Expense) -> int:
        if exp.amount_paise <= 0:
            raise ValidationError("Amount must be greater than zero")
        if not exp.description.strip():
            raise ValidationError("Description cannot be empty")
        with self.transaction() as c:
            cur = c.execute(
                "INSERT INTO expenses (amount_paise, description, spent_on, "
                "category_id, group_id) VALUES (?, ?, ?, ?, ?)",
                (exp.amount_paise, exp.description.strip(),
                 exp.spent_on.isoformat(), exp.category_id, exp.group_id),
            )
        lastrowid = cur.lastrowid
        if lastrowid is None:
            raise DatabaseError("Expense could not be inserted")
        log.info("Added expense id=%s", lastrowid)
        return lastrowid

    def get_expense(self, expense_id: int) -> Expense:
        row = self.conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
        if row is None:
            raise NotFoundError(f"Expense {expense_id} not found")
        return Expense(row["amount_paise"], row["description"],
                       date.fromisoformat(row["spent_on"]),
                       row["category_id"], row["group_id"], row["id"])