from discord.ext.commands import Cog, Bot, Context, command, ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded

from os import listdir, getcwd

from utils import log


class Developer(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	async def cog_check(self, ctx: Context) -> bool:
		super().cog_check(ctx)

		return await self.bot.is_owner(ctx.author)


	async def format_cog_error(self, error: Exception) -> str:
		error_message: str = "```bash\n"
		
		if type(error) == ExtensionNotFound:
			error_message += "Cog not found!"
		elif type(error) == ExtensionAlreadyLoaded:
			error_message += "Cog already loaded!"
		elif type(error) == ExtensionNotLoaded:
			error_message += "Cog isn't loaded!"
		else:
			error_message += str(error)

			log("error", "command 'load' raised an error:")
			print(error.with_traceback())

		error_message += "\n```"

		return error_message


	async def load_cog(self, cog: str) -> Exception | bool:
		try:
			await self.bot.load_extension(cog)
		except Exception as error:
			return error
		else:
			return True

	@command(help="Load cog(s)", aliases=['l'])
	async def load(self, ctx: Context, *cogs) -> None:
		try: await ctx.message.delete()
		except: pass

		if (not (cogs)) or (cogs[0].lower() == "all".lower()):
			for cog in listdir(f"{getcwd()}/cogs"):
				if cog.endswith('.py'):
					cog = cog[:-3]

					result: Exception | bool = await self.load_cog(f"cogs.{cog}")

					if result == True:
						await ctx.send(f":white_check_mark: loaded `{cog}`.", delete_after=5)
					else:
						error: str = await self.format_cog_error(result)
						await ctx.send(f":warning: failed to load `{cog}`:\n{error}")

		for cog in cogs:
			result: Exception | bool = await self.load_cog(f"cogs.{cog}")

			if result == True:
				await ctx.send(f":white_check_mark: loaded `{cog}`.", delete_after=5)
			else:
				error: str = await self.format_cog_error(result)

				await ctx.send(f":warning: failed to load `{cog}`:\n{error}")


	async def reload_cog(self, cog: str) -> str | bool:
		try:
			await self.bot.reload_extension(cog)
		except Exception as error:
			return error
		else:
			return True

	@command(help="Reload cog(s)", aliases=['r'])
	async def reload(self, ctx: Context, *cogs) -> None:
		try: await ctx.message.delete()
		except: pass

		if (not (cogs)) or (cogs[0].lower() == "all".lower()):
			for cog in listdir(f"{getcwd()}/cogs"):
				if cog.endswith('.py'):
					cog = cog[:-3]

					result: Exception | bool = await self.reload_cog(f"cogs.{cog}")

					if result == True:
						await ctx.send(f":white_check_mark: reloaded `{cog}`.", delete_after=5)
					else:
						error: str = await self.format_cog_error(result)
						await ctx.send(f":warning: failed to reload `{cog}`:\n{error}")

		for cog in cogs:
			result: Exception | bool = await self.reload_cog(f"cogs.{cog}")

			if result == True:
				await ctx.send(f":white_check_mark: reloaded `{cog}`.", delete_after=5)
			else:
				error: str = await self.format_cog_error(result)

				await ctx.send(f":warning: failed to reload `{cog}`:\n{error}")


	async def unload_cog(self, cog: str) -> str | bool:
		try:
			await self.bot.unload_extension(cog)
		except Exception as error:
			return error
		else:
			return True

	@command(help="Unload cog(s)", aliases=['u'])
	async def unload(self, ctx: Context, *cogs) -> None:
		try: await ctx.message.delete()
		except: pass

		if (not (cogs)) or (cogs[0].lower() == "all".lower()):
			for cog in listdir(f"{getcwd()}/cogs"):
				if cog.endswith('.py'):
					cog = cog[:-3]

					if cog.lower() == "developer":
						await ctx.send(f":warning: cog `developer` is too sensitive to be unloaded!", delete_after=5)

						continue

					result: Exception | bool = await self.unload_cog(f"cogs.{cog}")

					if result == True:
						await ctx.send(f":white_check_mark: unloaded `{cog}`.", delete_after=5)
					else:
						error: str = await self.format_cog_error(result)
						await ctx.send(f":warning: failed to unload `{cog}`:\n{error}")

		for cog in cogs:
			if cog.lower() == "developer":
				await ctx.send(f":warning: cog `developer` is too sensitive to be unloaded!", delete_after=5)

				continue

			result: Exception | bool = await self.unload_cog(f"cogs.{cog}")

			if result == True:
				await ctx.send(f":white_check_mark: unloaded `{cog}`.", delete_after=5)
			else:
				error: str = await self.format_cog_error(result)

				await ctx.send(f":warning: failed to unload `{cog}`:\n{error}")



async def setup(bot: Bot) -> None:
	await bot.add_cog(Developer(bot))