__all__ = ['Database'] # whatever u put here will be imported when an everything import is attempted "from x import *"

from __future__ import annoations # makes it so we can pass "Database" as a return type.

from asyncpg.pool import Pool
from asyncpg.connection import Connection # not sure about this


class Database:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool
        self.connection: Connection | None = None

    async def __aenter__(self) -> "Database":
        self.connection = self.pool.acquire()

        return self

    async def __aexit__(self, *args) -> None:
        await self.connection.close()


    async def get_user(user_id: int) -> list:
        assert self.connection != None # makes sure we got a connection

        query: str = "SELECT * FROM users WHERE id = $1"

        return await self.connection.fetchrow(query, user_id)
