__all__ = ['get_db_latency', 'fetch_guild', 'fetch_user', 'update_user', 'user_add_server', 'get_guild_adembed', 'update_guild_adembed', 'update_guild_invite_url', 'update_guild_adchannel', 'create_guild']

from asyncpg.pool import Pool
from time import time

from .errors import DBGuildNotFound, DBUserNotFound, DBInvalidColumn, DBDataAlreadyExists
from .default import Default
from json import loads, dumps


async def get_db_latency(pool: Pool) -> float:
	old: float = time()

	async with pool.acquire() as conn:
		await conn.execute("SELECT now()")

	return time() - old


async def fetch_guild(pool: Pool, guild_id: str | int) -> dict:
	guild_id = int(guild_id)

	async with pool.acquire() as conn:
		try:
			data = dict(await conn.fetchrow("SELECT * FROM servers WHERE id = $1", guild_id))
		except:
			raise DBGuildNotFound

	return data


async def create_guild(pool: Pool, guild_id: str | int, **kwargs) -> None:
	guild_id = int(guild_id)

	async with pool.acquire() as conn:
		await conn.execute(f"UPDATE servers SET id = $1", guild_id)


async def update_guild_adchannel(pool: Pool, guild_id: str | int, channel_id: str | int) -> None:
	async with pool.acquire() as conn:
		await conn.execute(f"UPDATE servers SET ad_channel = $1 WHERE id = $2", str(channel_id), int(guild_id))


async def fetch_user(pool: Pool, user_id: str | int) -> dict:
	user_id = int(user_id)

	async with pool.acquire() as conn:
		try:
			data = dict(await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id))
		except:
			raise DBUserNotFound

	return data


async def update_user(pool: Pool, user_id: str | int, **kwargs) -> None:
	user_id = int(user_id)
	
	user_data: dict = {}
	
	if "user_data" in list(kwargs.keys()):
		user_data = kwargs["user_data"]
	else:
		user_data = await fetch_user(pool, user_id)

	async with pool.acquire() as conn:
		for column, value in kwargs.items():
			if column == "user_data": continue

			if column not in Default.USER_COLUMNS:
				raise DBInvalidColumn(column)

			await conn.execute(f"UPDATE users SET {column} = $1 WHERE id = $2", value, user_id)


async def user_add_server(pool, user_id: str | int, server_id: str | int, **kwargs) -> None:
	user_id = int(user_id)
	server_id = str(server_id)

	user_data: dict = {}

	if "user_data" in list(kwargs.keys()):
		user_data = kwargs["user_data"]

	else:
		user_data = await fetch_user(pool, user_id)

	if server_id in user_data["servers"]:
		raise DBDataAlreadyExists(f"server '{server_id}' already exists in user '{user_id}' servers")

	else:
		new_servers: list = user_data["servers"]
		new_servers.append(server_id)

		await update_user(pool, user_id, servers=new_servers)


async def get_guild_adembed(pool: Pool, server_id: int, field: str = None) -> dict | str:
	query: str = "SELECT ad_embed FROM servers WHERE id = $1"

	if field:
			query = f"SELECT ad_embed::json->>'{field}' FROM servers WHERE id = $1"
	
	async with pool.acquire() as connection:
		if field:
			return dict(await connection.fetchrow(query, server_id))["?column?"]
		else:
			return loads(dict(await connection.fetchrow(query, server_id))["ad_embed"])


async def update_guild_adembed(pool: Pool, server_id: int, embed: dict) -> None:
	async with pool.acquire() as connection:
		await connection.execute("UPDATE servers SET ad_embed = $2 WHERE id = $1", server_id, dumps(embed))


async def update_guild_invite_url(pool: Pool, server_id: int, url: str) -> None:
	async with pool.acquire() as connection:
		await connection.execute("UPDATE servers SET guild_invite_url = $2 WHERE id = $1", server_id, url)