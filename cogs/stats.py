from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Member

from random import randint

from utils import Default


class Stats(GroupCog, name="stats"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="View the guild's stats")
	@guilds(Default.SERVER)
	async def guild(self, inter: Interaction) -> None:
		members_count: int = inter.guild.member_count or 0

		embed = Embed(title="Stats", description=f":zap: **Guild-Activity:** `{members_count * randint(1,1000000)}`", color=Default.COLOR)

		embed.set_author(name=inter.guild.name, icon_url=inter.guild.icon.url if inter.guild.icon else "")
		embed.set_footer(text=Default.FOOTER)
		embed.set_image(url=inter.guild.banner.url if inter.guild.banner else "")

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


async def setup(bot: Bot) -> None:
	await bot.add_cog(Stats(bot), guilds=[Default.SERVER])