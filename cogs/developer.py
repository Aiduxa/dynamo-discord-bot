from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import command as slash_command, guilds, describe
from discord import Interaction
from traceback import print_tb

from utils import Default, log


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


	@slash_command(description="Developer command")
	@guilds(Default.SERVER)
	@describe(message="Reloads a cog or cogs")
	async def reload(self, inter: Interaction, *args) -> None:
		for cog in args:

			try:
				await self.bot.reload_extension(f"cogs.{cog[:-3]}")
				log("status", f"reloaded '{cog}'")

			except Exception as e:
				log("error", f"failed to reload '{cog}'")
				print_tb(e)
			
		else:
			await inter.response.send_message("Reloaded cog(s) :white_check_mark:")






async def setup(bot: Bot) -> None:
	await bot.add_cog(Developer(bot))