from asyncpg.pool import Pool

from traceback import print_tb

"""
Notes for myself:

use acquire() when using a singular query execution

"""

async def create_user(pool: Pool, user_id: int, servers_ids: list[int]) -> None:
	async with pool.acquire() as connection:
		await connection.execute("INSERT INTO users(id, servers) VALUES ($1, $2,)", user_id, servers_ids)


async def update_user(pool: Pool, user_id: int, column: str, value: any) -> None:
	async with pool.acquire() as connection:
		await connection.execute(f"UPDATE users SET {column} = $1 WHERE id = $2", value, user_id)

async def get_user(pool : Pool, user_id : int) -> list:
	async with pool.acquire() as connection:
		return await connection.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

async def delete_user(pool: Pool, user_id: int) -> None:
	async with pool.acquire() as connection:
		await connection.execute("DELETE FROM users WHERE id = $1", user_id)



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
			


