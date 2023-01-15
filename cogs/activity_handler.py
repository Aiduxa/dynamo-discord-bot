from discord.ext.commands import Bot, Cog
from discord.ext.tasks import loop
from discord import Message, VoiceChannel, DMChannel, GroupChannel, Guild, Member
from datetime import datetime, timedelta

from utils import fetch_guild, DBGuildNotFound, fetch_user, DBUserNotFound, update_user, user_add_server, Default # create_user


class ActivityHandler(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		self.background_handler.start()

		super().__init__()

	
	@loop(hours=24)
	async def background_handler(self) -> None:
		for user in self.bot.users:
		
			try:
				user_data: dict = await fetch_user(self.bot.POOL, user.id)
			except DBUserNotFound:
				return

			last_day_msgs: int = user_data["last_day_messages"]
			activity_rank: int = 0

			if last_day_msgs >= 1000:
				activity_rank = 3

			elif last_day_msgs >= 100:
				activity_rank = 2

			else:
				activity_rank = 1

			await update_user(self.bot.POOL, user.id, last_day_messages=0, activity_rank=activity_rank)


	async def handler(self, message: Message) -> None:
		if message.channel in [VoiceChannel, DMChannel, GroupChannel]: return
		if message.is_system(): return
		if message.author.bot: return

		server: Guild = message.guild

		try:
			guild: dict = fetch_guild(self.bot.POOL, server.id)
		except DBGuildNotFound:
			return

		user: Member = message.author
		user_data: dict = {}

		try:
			user_data = fetch_user(self.bot.POOL, user.id)
		except DBUserNotFound:
			# user_data = create_user(self.bot.POOL, user.id, servers=[str(server.id)])
			await message.channel.send("implement create_user u lazy fuck")
			
			return
		else:
			if str(guild.id) not in user_data["servers"]:
				user_add_server(self.bot.POOL, user.id, server.id)

		last_message: datetime = (datetime.strptime(user_data["last_message"], Default.DATETIME_FORMAT) - datetime.utcnow())

		if last_message < timedelta(minutes=1): return

		await update_user(self.bot.POOL, user.id, last_message=str(datetime.utcnow()), last_day_messages=user_data["last_day_messages"] + 1)


	async def setup(bot: Bot) -> None:
		cog = ActivityHandler(bot)

		bot.add_listener(cog.handler, 'on_message')

		await bot.add_cog(cog)


async def setup(bot: Bot) -> None:
	await bot.add_cog(ActivityHandler(bot))