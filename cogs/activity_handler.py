from discord.ext.commands import Bot, Cog
from discord.ext.tasks import loop
from discord import Message, TextChannel
from datetime import datetime, timedelta

from utils import fetch_user, DBUserNotFound, Default, update_user_server_last_message, update_user_server_messages, update_user_activity_ranks, create_user, log


class ActivityHandler(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		self.background_handler.start()

		super().__init__()

	
	@loop(hours=24)
	async def background_handler(self) -> None:
		log("debug", "started background activity handler")

		for user in self.bot.users:
			try:
				user_data: dict = await fetch_user(self.bot.POOL, user.id)
			except DBUserNotFound:
				continue

			new_activity_ranks: dict = {}

			# server_messages
			for server_id, messages in user_data["servers_messages"].items():
				if messages >= 100:
					new_activity_ranks[server_id] = 1
				elif messages >= 1000:
					new_activity_ranks[server_id] = 2
				else:
					new_activity_ranks[server_id] = 0

				await update_user_server_messages(self.bot.POOL, user.id, server_id, 0, user_data)

				log("debug", "updated server messages")

			if new_activity_ranks == {}:
				continue

			# server activity ranks
			for server_id in list(user_data["activity_ranks"].keys()):
				if server_id in list(new_activity_ranks.keys()):
					await update_user_activity_ranks(self.bot.POOL, user.id, server_id, new_activity_ranks[server_id], user_data)

					log("debug", "updated server activity rank")

		log("debug", "finished background activity handker")




	async def handler(self, message: Message) -> None:
		log("debug", "started on_message activity handler")

		if type(message.channel) != TextChannel:
			log("debug", "channel wasn't a text channel")

			return

		if message.author.bot:
			log("debug", "user was not human")

			return

		user_data: dict | None = None

		try:
			user_data = await fetch_user(self.bot.POOL, message.author.id)
		except DBUserNotFound:
			user_data = await create_user(self.bot.POOL, message.author.id)

		if user_data == None:
			log("debug", "couldn't get user data")

			return

		servers_last_message: dict = user_data["servers_last_message"]

		if str(message.guild.id) not in list(servers_last_message.keys()):
			await update_user_server_last_message(self.bot.POOL, message.author.id, message.guild.id, datetime.utcnow(), user_data)

			await update_user_server_messages(self.bot.POOL, message.author.id, message.guild.id, 1, user_data)

			await update_user_activity_ranks(self.bot.POOL, message.author.id, message.guild.id, 0, user_data)

			log("debug", "created new server entry for user servers")

			return

		if (datetime.utcnow() + timedelta(minutes=1)) < datetime.strptime(servers_last_message[str(message.guild.id)], Default.FORMAT):
			log("debug", "confirmed user is still on cooldown")

			return

		await update_user_server_last_message(self.bot.POOL, message.author.id, message.guild.id, datetime.utcnow(), user_data)

		server_messages = user_data["servers_messages"][str(message.guild.id)]

		await update_user_server_messages(self.bot.POOL, message.author.id, message.guild.id, server_messages + 1, user_data)

		log("debug", "finished on_message activity handler")


async def setup(bot: Bot) -> None:
	cog = ActivityHandler(bot)

	bot.add_listener(cog.handler, 'on_message')

	await bot.add_cog(cog)