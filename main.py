from os import environ, getcwd, listdir
from traceback import print_tb

from discord import Activity, ActivityType, Status, Intents
from discord.ext.commands import Bot, when_mentioned_or, DefaultHelpCommand
from discord.ext.tasks import loop

from asyncpg.pool import Pool
from asyncpg import create_pool

from dotenv import load_dotenv

load_dotenv(f"{getcwd()}/utils/.env")

from utils import Default, log, database


class Dynamo(Bot):
	def __init__(self, intents: Intents) -> None:
			self.POOL: Pool | None = None

			super().__init__(
				command_prefix=when_mentioned_or(Default.PREFIX),
				case_sensitive=False,
				status=Status.online,
				intents=intents,
				application_id=environ.get("app_id"),
				description="User engagement bot",
			)

	
	@loop(seconds=30.0)
	async def continous_handler(self) -> None:
		await self.change_presence(activity=Activity(name=f"{len(self.users)} members", type=ActivityType.watching))

	@continous_handler.before_loop
	async def before_continous_handler(self) -> None:
		log("status", "waiting to start 'continous_handler'")
		
		await self.wait_until_ready()

		log("status", "started 'continous_handler'")


	async def on_ready(self) -> None:
		log("status", "running")

	async def setup_hook(self) -> None:
		# initalizing database
		db_config = {
		 	'dsn': environ.get("postgres_dsn"),
		 	'user': environ.get("postgres_user"),
		 	'password': environ.get("postgres_password"),
		 	'host': environ.get("postgres_host"),
		 	'database': environ.get("postgres_db"),
		 	'port': environ.get("postgres_port")
		}

		try:
			self.POOL = await create_pool(**db_config)
		except Exception as e:
			log("error", f"failed to initialise the database")
			print_tb(e)
		else:
			log("status", "database initialised")

		# loading cogs
		for cog in listdir(f"{getcwd()}/cogs"):
			if not cog.endswith(".py"):
				continue

			try:
				await self.load_extension(f"cogs.{cog[:-3]}")
			except Exception as e:
				log("error", f"failed to load '{cog}'")
				print_tb(e)
			else:
				log("status", f"loaded '{cog}'")

		# syncing commands
		try:
			await self.tree.sync()
			await self.tree.sync(guild=Default.SERVER)
		except Exception as e:
			log("error", "failed to sync commands")
			print_tb(e)
		else:
			log("status", "synced commands")

		# running background task
		self.continous_handler.start()


intents: Intents = Intents.default()
intents.members = True
intents.messages = True

bot = Dynamo(intents)


if __name__ == '__main__':
	bot.run(environ.get("token"))
