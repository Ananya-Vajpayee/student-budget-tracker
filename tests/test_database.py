import os
import sys
import unittest
from datetime import date

# Make the src/ folder importable when running tests from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import Database
from models import Expense
from exceptions import ValidationError, NotFoundError


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Fresh in-memory database for every test
        self.db = Database(":memory:")

    def test_add_and_get_expense(self):
        exp = Expense(25000, "Swiggy dinner", date(2026, 10, 2))
        new_id = self.db.add_expense(exp)
        fetched = self.db.get_expense(new_id)
        self.assertEqual(fetched.amount_paise, 25000)
        self.assertEqual(fetched.description, "Swiggy dinner")
        self.assertEqual(fetched.spent_on, date(2026, 10, 2))

    def test_zero_amount_rejected(self):
        with self.assertRaises(ValidationError):
            self.db.add_expense(Expense(0, "Nothing", date(2026, 10, 2)))

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValidationError):
            self.db.add_expense(Expense(-500, "Refund?", date(2026, 10, 2)))

    def test_empty_description_rejected(self):
        with self.assertRaises(ValidationError):
            self.db.add_expense(Expense(100, "   ", date(2026, 10, 2)))

    def test_missing_expense_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            self.db.get_expense(999)


if __name__ == "__main__":
    unittest.main()