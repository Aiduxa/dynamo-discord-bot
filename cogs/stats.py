from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed
from discord import __version__ as dpyversion
from platform import system, release
from psutil import cpu_percent, cpu_count, virtual_memory
from sys import version

from utils import Default, get_db_latency


class Stats(GroupCog, name="stats"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	# async def guild_autocomplete(self, _inter: Interaction, current: Guild) -> list[Choice[str]]:
	# 	return [Choice(name=guild.name, value=str(guild.id)) for guild in self.bot.guilds if current.lower() in guild.name.lower()][:25]

	# @command(description="View the guild's stats")
	# @guilds(Default.SERVER)
	# @autocomplete(guild=guild_autocomplete)
	# async def guild(self, inter: Interaction, guild: str | None = None) -> None:


	# @command(description="View your stats")
	# @guilds(Default.SERVER)
	# async def member(self, inter: Interaction, member: Member | None) -> None:
	# 	await inter.response.send_message(ephemeral=True)


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
