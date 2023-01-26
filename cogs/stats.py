from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds, Choice, autocomplete
from discord import Interaction, Embed, Member, Guild
from discord import __version__ as dpyversion
from discord.utils import find as discord_find
from platform import system, release
from psutil import cpu_percent, cpu_count, virtual_memory
from sys import version

from utils import Default, Emoji, get_db_latency, fetch_user, fetch_guild, DBGuildNotFound, DBUserNotFound, create_user, create_guild
    

class Stats(GroupCog, name="stats"):

	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		super().__init__()
		
	async def guild_autocomplete(self, _inter: Interaction, current: Guild) -> list[Choice[str]]:
		return [Choice(name=guild.name, value=str(guild.id)) for guild in self.bot.guilds if current.lower() in guild.name.lower()][:25]

	@command(description="View the guild's stats")
	@guilds(Default.SERVER)
	@autocomplete(guild=guild_autocomplete)
	async def guild(self, inter: Interaction, guild: str | None = None) -> None:
		guild: Guild = await self.bot.fetch_guild(int(guild)) if guild else inter.guild
		
		guild_data: dict = {}
		
		try:
			guild_data = await fetch_guild(self.bot.POOL, guild.id)
		except DBGuildNotFound:
			guild_data = await create_guild(self.bot.POOL, guild.id)

		guild_users: list[list[str]] = guild_data['guild_users']

		for i in range(3):
			if len(guild_users) < (i + 1):
				guild_users.append([])

		embed = Embed(
			title=f"{guild.name}'s statistics",
			description=f"{Emoji.POWER} `{guild_data['activity_power']}`\n\n{Emoji.SUPER_ACTIVE} **Super active:** `{len(guild_users[2])}`\n{Emoji.ACTIVE} **Active:** `{len(guild_users[1]) or 0}`\n{Emoji.ONLINE} **Online:** `{len(guild_users[0])}`",
			color=Default.COLOR
		)

		embed.set_footer(text=Default.FOOTER)
		embed.set_thumbnail(url=guild.icon.url)

		await inter.response.send_message(embed=embed, ephemeral=True)


	@command(description="View your stats")
	@guilds(Default.SERVER)
	async def member(self, inter: Interaction, member: Member | None) -> None:
		user = member if member else inter.user

		user_data: dict = {}

		try:
			user_data = await fetch_user(self.bot.POOL, user.id)
		except DBUserNotFound:
			user_data = await create_user(self.bot.POOL, user.id)

		embed = Embed(
			title=f"{user.name}'s statistics",
			description=f"{Emoji.CURRENCY} `{user_data['gems']}`",
			color=Default.COLOR
		)

		embed.set_footer(text=Default.FOOTER)
		embed.set_thumbnail(url=user.avatar.url)

		# Loops through user's servers, gets server, it's messages, title, user's activity rank
		for server_id in dict(user_data["servers_messages"]).keys():
			guild = discord_find(lambda g: g.id == int(server_id), self.bot.guilds)
			
			if not guild:
				"""Guild was not found"""
				continue

			guild_data: dict = {}

			try:
				guild_data = await fetch_guild(self.bot.POOL, server_id)		
			except DBGuildNotFound:
				guild_data = await create_guild(self.bot.POOL, server_id)

			raw_activity_rank: int = user_data["activity_ranks"][server_id]

			# activity_rank value to emoji

			if raw_activity_rank == 2:
				activity_rank: str = f"{Emoji.SUPER_ACTIVE} `super active`"
			elif raw_activity_rank == 1:
				activity_rank: str = f"{Emoji.ACTIVE} `active`"
			else:
				activity_rank: str = f"{Emoji.ONLINE} `online`"

			embed.add_field(
				name=f"***{guild.name}*  ({Emoji.POWER} `{guild_data['activity_power']}`)**",
				value=f"\nActivity rank: {activity_rank}\nTotal sent messages: `{user_data['servers_messages'][server_id]}`"
			)

		await inter.response.send_message(embed=embed, ephemeral=True)


	@command(description="View bot's statistics (aka for nerds)'")
	@guilds(Default.SERVER)
	async def bot(self, inter: Interaction):
		latency: float = round(self.bot.latency * 1000, 2)

		raw_db_latency: float = await get_db_latency(self.bot.POOL) 
		database_latency: float = round(raw_db_latency * 1000, 2)

		os: str = system()
		os_release: str = release()

		cpu_usage: float = cpu_percent()

		ram_total_gb: int = int(virtual_memory()[0] / 1000000)
		ram_usage_percent: float = virtual_memory()[2]
		ram_usage_gb: int = int(virtual_memory()[3] / 1000000)

		embed = Embed(
			title="**Bot's information**",
			description=f"\n**Latency:** ``{latency}ms``\n**Database Latency:** ``{database_latency}ms``\n**Python version:** ``{version}``\n**Discord.py version:** ``{dpyversion}``",
			color=Default.COLOR
		)

		embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar.url)
		embed.set_footer(text=Default.FOOTER)

		embed.add_field(name="OS", value=f"``{os} {os_release}``")
		embed.add_field(name="CPU", value=f"**Usage:** ``{cpu_usage}%/100%``\n**Count:** ``{cpu_count()}``", inline=True)
		embed.add_field(name="RAM", value=f"**Usage:** ``{ram_usage_gb}Mb/{ram_total_gb}Mb ({ram_usage_percent}%/100%) ``")

		await inter.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Stats(bot), guilds=[Default.SERVER])
