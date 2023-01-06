from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds, autocomplete, Choice
from discord import Interaction, Embed, Member, Guild
from discord import __version__ as dpyversion
from platform import system, release
from psutil import cpu_percent, cpu_count, virtual_memory
from sys import version

from random import randint

from utils import Default, database


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
		if guild != None:
			guild = await self.bot.fetch_guild(int(guild))
		else:
			guild = inter.guild

		members_count: int = guild.member_count or 0

		embed = Embed(title="Stats", description=f":zap: **Guild-Activity:** `{members_count * randint(1,1000000)}`", color=Default.COLOR)

		embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else "")
		embed.set_footer(text=Default.FOOTER)
		embed.set_image(url=guild.banner.url if guild.banner else "")

		ranked_members: str = "`0` :blue_square: **Super-Active**\n`0` :green_square: **Active**\n`0` :red_square: **Unactive**"

		embed.add_field(name=f"Users (`{members_count if members_count != 0 else 'N/A'}`):", value=ranked_members, inline=False) # members_count requires "members" intent. so it could be None.

		await inter.response.send_message(embed=embed, ephemeral=True)


	@command(description="View your stats")
	@guilds(Default.SERVER)
	async def member(self, inter: Interaction, member: Member | None) -> None:
		user: Member = member if member != None else inter.user
		
		embed = Embed(title="Stats", description=f":gem: **Gems:** `{randint(1,10000)}`\n:blue_square: **Active**", color=Default.COLOR)

		embed.set_author(name=user, icon_url=user.display_avatar.url)
		embed.set_footer(text=Default.FOOTER)

		await inter.response.send_message(embed=embed, ephemeral=True)

	@command(description="View bot status")
	@guilds(Default.SERVER)
	async def bot(self, inter: Interaction):

		latency: float = round(self.bot.latency* 1000, 2) 
		database_latency: float = round(await database.latency(self.bot.POOL) * 1000, 2)

		os: str = system()
		osrelease: str = release()

		cpu_usage: float = cpu_percent()

		ram_total_gb: int = int(virtual_memory()[0]/1000000)
		ram_usage_percent: float = virtual_memory()[2]
		ram_usage_gb: int = int(virtual_memory()[3]/1000000)

		embed = Embed(
			title="**Bot's information**",
			description=f"\n**Latency:** ``{latency}ms``\n**Database Latency:** ``{database_latency}ms``\n**Python version:** ``{version}``\n**Discord.py version:** ``{dpyversion}``"
		)
		embed.add_field(
			name="OS",
			value=f"``{os} {osrelease}``"
		)
		embed.add_field(
			name="CPU",
			value=f"**Usage:** ``{cpu_usage}%/100%``\n**Count:** ``{cpu_count()}``",
			inline=True
		)
		embed.add_field(
			name="RAM",
			value=f"**Usage:** ``{ram_usage_gb}Mb/{ram_total_gb}Mb ({ram_usage_percent}%/100%) ``"
		)
		embed.set_author(name="Dynamo", icon_url=self.bot.user.display_avatar.url)
		embed.color = Default.COLOR
		embed.set_footer(text=Default.FOOTER)

		await inter.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: Bot) -> None:
	await bot.add_cog(Stats(bot), guilds=[Default.SERVER])