class BudgetError(Exception):
    """Base class for all app errors."""


class ValidationError(BudgetError):
    """Bad user input (amount, date, category...)."""


class NotFoundError(BudgetError):
    """Requested record does not exist."""


class DatabaseError(BudgetError):
    """Storage-layer failure (insert failed, connection problem...)."""