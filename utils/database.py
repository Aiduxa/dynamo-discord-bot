from __future__ import annotations
__all__ = ['Database']

from asyncpg.pool import Pool
from asyncpg.connection import Connection

from ..main import bot


class Database:
    def __init__(self) -> None:
        self.pool: Pool = bot.POOL
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
