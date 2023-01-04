from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import command as slash_command, guilds, describe
from discord import Interaction

from utils import Default


class Developer(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	async def cog_check(self, ctx: Context) -> bool:
		super().cog_check(ctx)

		return self.bot.is_owner()


	@slash_command(description="Developer command")
	@guilds(Default.SERVER)
	@describe(message="The message the bot will say")
	async def spk(self, inter: Interaction, message: str) -> None:
		await inter.response.send_message(message)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Developer(bot))