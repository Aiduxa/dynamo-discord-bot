from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Guild

from utils import Default


class Guild(GroupCog, name="guild"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="View the server's stats")
	@guilds(Default.SERVER)
	async def stats(self, inter: Interaction) -> None:
		embed = Embed(title="Stats", color=Default.COLOR)

		current_guild: Guild = inter.guild

		embed.set_author(name=current_guild.name, icon_url=current_guild.icon.url if current_guild.icon else "")
		embed.set_footer(text=Default.FOOTER)
		embed.set_image(url=current_guild.banner.url if current_guild.banner else "")

		ranked_members: str = "`0` :blue_square: **Super-Active**\n`0` :green_square: **Active**\n`0`:red_square: **Unactive**"

		embed.add_field(name=f"Users (`{current_guild.member_count or 'N/A'}`):", value=ranked_members, inline=False) # members_count requires "members" intent. so it could be None.

		await inter.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Guild(bot), guilds=[Default.SERVER])