__all__ = ['DBGuildNotFound', 'DBUserNotFound', 'DBInvalidColumn', 'DBDataAlreadyExists']


class DatabaseException(Exception):
    "Base database exception"
    pass

class DBGuildNotFound(DatabaseException):
    def __init__(self) -> None:
        super().__init__("guild not found in the database")

class DBUserNotFound(DatabaseException):
    def __init__(self) -> None:
        super().__init__("user not found in the database")

class DBInvalidColumn(DatabaseException):
    def __init__(self, column: str) -> None:
        super().__init__(f"column '{column}' not found")

class DBDataAlreadyExists(DatabaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)