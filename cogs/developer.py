from discord.ext.commands import Cog, Bot, Context, command, is_owner
from traceback import print_tb

from utils import Default, log


class Developer(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	async def cog_check(self, ctx: Context) -> bool:
		super().cog_check(ctx)

		return self.bot.is_owner()


	@command(description="Developer command")
	@is_owner()
	async def reload(self, ctx, *args) -> None:
		for cog in args:
			try:
				await self.bot.reload_extension(f"cogs.{cog[:-3]}")
				log("status", f"reloaded '{cog}'")

			except Exception as e:
				log("error", f"failed to reload '{cog}'")
				print_tb(e)
			
		else:
			await ctx.send("Reloaded cog(s) :white_check_mark:")






async def setup(bot: Bot) -> None:
	await bot.add_cog(Developer(bot))