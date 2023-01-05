import asyncio
import asyncpg

from utils.database import pool as sql

async def user(id) -> None:

    def __init__(self, id) -> None:
        pass

    async def get(id) -> None:
        
        query: str = "SELECT * FROM users WHERE id = $1"

        async with sql.POOL.acquire as db:

            data: [list] = [await db.fetchrow(query, id)]
 
            return data



