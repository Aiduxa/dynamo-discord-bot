from discord.ext.commands import GroupCog, Bot, GuildNotFound
from discord.app_commands import command, guilds, Transformer, Transform
from discord import Interaction, Embed, Member, Guild
from discord.utils import get, find
from discord import __version__ as dpyversion
from platform import system, release
from psutil import cpu_percent, cpu_count, virtual_memory
from sys import version
from typing import NamedTuple

from utils import Default, Emoji, get_db_latency, fetch_user, fetch_guild, get_guild_adembed

# Transforms an argument into raw type
class Point(NamedTuple):
    x: str
    y: str
    
class PointTransformer(Transformer):
    async def transform(self, inter: Interaction, value: str) -> Point:
        (x, _, y) = value.partition(",")
        return Point(x=str(x.strip()), y=str(y.strip()))
    

class Stats(GroupCog, name="stats"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		super().__init__()
  
	# Ur fucking shit doesn't work fella, neither do I understand it

	# async def guild_autocomplete(self, _inter: Interaction, current: Guild) -> list[Choice[str]]:
	#  	return [Choice(name=guild.name, value=str(guild.id)) for guild in self.bot.guilds if current.lower() in guild.name.lower()][:25]

	@command(description="View the guild's stats")
	@guilds(Default.SERVER)
	async def guild(self, inter: Interaction, guild: Transform[Point, PointTransformer] | None = None) -> None:

		if isinstance(guild, str):
			if guild.is_digit():
				try:
					guild = get(self.bot.guilds, id=guild)
				except GuildNotFound:
					await inter.response.send_message("Supplied guild was not found, check your typing and try again!")
		elif isinstance(guild, str):
			try:
				guild = get(self.bot.guilds, name=guild)
			except GuildNotFound:
				await inter.response.send_message("Supplied guild was not found, check your typing and try again!")
		else:
			guild = inter.guild

		guild_data: dict = await fetch_guild(self.bot.POOL, guild.id)

		super_active: int = 0
		active: int = 0
		online: int = 0

		# Counts activity ranks
		for user in guild_data["guild_users"]:
			user_data: dict = await fetch_user(self.bot.POOL, str(user[0]))
			if user_data["activity_ranks"][str(guild.id)] == 0: online += 1
			elif user_data["activity_ranks"][str(guild.id)] == 1: active += 1
			elif user_data["activity_ranks"][str(guild.id)] == 2: super_active += 1


		embed = Embed(
			title=f"{guild.name}'s statistics",
			description=f"**Power:** ``{guild_data['activity_power']}`` {Emoji.POWER}\n\n{Emoji.SUPER_ACTIVE} **Super active:** ``{super_active}``\n {Emoji.ACTIVE} **Active:** ``{active}``\n {Emoji.ONLINE} **Online:** ``{online}``\n\n ",
			color=Default.COLOR
		)
		embed.set_footer(text=Default.FOOTER)
  
		await inter.response.send_message(embed=embed, ephemeral=True)


	@command(description="View your stats")
	@guilds(Default.SERVER)
	async def member(self, inter: Interaction, member: Member | None) -> None:

		if not member:
			member = inter.user

		user_data: dict = await fetch_user(self.bot.POOL, member.id)

		embed = Embed(
			title=f"{member.name}'s statistics",
			description=f"{user_data['gems']} {Emoji.CURRENCY}",
			color=Default.COLOR
		)
		embed.set_footer(text=Default.FOOTER)

		# Loops through user's servers, gets server, it's messages, title, user's activity rank
		for id in dict(user_data["servers_messages"]).keys():
			guild = find(lambda g: g.id == int(id), self.bot.guilds)
			if not guild:
				"""Guild was not found"""
				continue
			guild_data = await fetch_guild(self.bot.POOL, id)
			activity_rank: int = user_data["activity_ranks"][id]
			total_messages: int = user_data["servers_messages"][id]

			# activity_rank value to emoji

			if activity_rank == 1:
				activity_rank: str = Emoji.ACTIVE
			elif activity_rank == 2:
				activity_rank: str = Emoji.SUPER_ACTIVE
			else:
				activity_rank: str = Emoji.ONLINE

			embed.add_field(
				name=f"***{guild.name}*** **({Emoji.POWER} ``{guild_data['activity_power']}``)**",
				value=f"\n*Activity rank:* {activity_rank}\n*Total sent messages:* ``{total_messages}``"
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
