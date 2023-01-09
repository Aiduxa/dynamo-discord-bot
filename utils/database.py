from time import time
from asyncpg.pool import Pool
from json import dumps, loads

from traceback import print_tb

"""
Notes for myself:

use acquire() when using a singular query execution

"""

async def latency(pool: Pool) -> float:
	async with pool.acquire() as connection:
		old: float = time()
		await connection.execute("SELECT now()")
		return time()-old

async def create_user(pool: Pool, user_id: int, servers_ids: list[int]) -> None:
	async with pool.acquire() as connection:
		await connection.execute("INSERT INTO users(id, servers) VALUES ($1, $2,)", user_id, servers_ids)


async def update_user(pool: Pool, user_id: int, column: str, value: any) -> None:
	async with pool.acquire() as connection:
		await connection.execute(f"UPDATE users SET {column} = $1 WHERE id = $2", value, user_id)

async def get_user(pool: Pool, user_id: int) -> list:
	async with pool.acquire() as connection:
		return await connection.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

async def delete_user(pool: Pool, user_id: int) -> None:
	async with pool.acquire() as connection:
		await connection.execute("DELETE FROM users WHERE id = $1", user_id)

async def get_adembed(pool: Pool, server_id: int, field: str = None) -> dict | str:
	query: str = "SELECT ad_embed FROM servers WHERE id = $1"

	if field:
			query = f"SELECT ad_embed::json->>'{field}' FROM servers WHERE id = $1"
	
	async with pool.acquire() as connection:
		if field:
			return dict(await connection.fetchrow(query, server_id))["?column?"]
		else:
			return loads(dict(await connection.fetchrow(query, server_id))["ad_embed"])

async def update_adembed(pool: Pool, server_id: int, embed: dict) -> None:
	async with pool.acquire() as connection:
		await connection.execute("UPDATE servers SET ad_embed = $2 WHERE id = $1", server_id, dumps(embed))

async def get_guild_invite_url(pool: Pool, server_id: int) -> str:
	async with pool.acquire() as connection:
		return await connection.fetchrow("SELECT guild_invite_url FROM servers WHERE id = $1", server_id)

async def update_guild_invite_url(pool: Pool, server_id: int, url: str) -> None:
	async with pool.acquire() as connection:
		await connection.execute("UPDATE servers SET guild_invite_url = $2 WHERE id = $1", server_id, url)

async def execute(pool: Pool, query: str, *args) -> list | None:
	async with pool.acquire() as connection:
		result: list = None
		try:
			if args:
				result: list = [connection.fetch(query, *args)]
			else:
				await connection.execute(query)
		except Exception as e: print_tb(e)
		else: return result
			


