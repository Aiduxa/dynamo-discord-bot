
from discord import Interaction
from discord.ext.commands import Cog, Bot, Context, is_owner
from discord.app_commands import command
from traceback import print_tb

from utils import Default, log, database


class Developer(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	async def cog_check(self, ctx: Context) -> bool:
		super().cog_check(ctx)

		return self.bot.is_owner()


	@command(description="Developer command")
	@is_owner()
	async def reload(self, inter : Interaction, cog : str) -> None:
		try:
			await self.bot.reload_extension(f"cogs.{cog[:-3]}")
			log("status", f"reloaded '{cog}'")

		except Exception as e:
			log("error", f"failed to reload '{cog}'")
			print_tb(e)
		
		else:
			await inter.response.send_message("Reloaded cog(s) :white_check_mark:")

	@command(description="Developer command")
	@is_owner()
	async def custom(self, inter: Interaction, query: str, *args) -> None:
		msg: str = ""

		msg = await database.execute(self.bot.POOL, query, *args)

		await inter.response.send_message(msg, ephemeral=True)




async def setup(bot: Bot) -> None:
	await bot.add_cog(Developer(bot))