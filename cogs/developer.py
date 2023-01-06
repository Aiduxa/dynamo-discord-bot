from discord.ext.commands import Cog, Bot, Context, command, ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded
from discord import File, Embed, Member, Interaction, ButtonStyle
from discord.ui import View, button, Button

from os import listdir, getcwd
from io import StringIO, BytesIO
from functools import partial
from traceback import format_exception

from utils import Default, log


class shutdownView(View):
	def __init__(self, author: Member) -> None:
		self.author = author
		self.stop_shutdown: bool = False

		super().__init__(timeout=60.0)

	
	async def interaction_check(self, inter: Interaction) -> bool:
		return self.author.id == inter.user.id


	@button(label="Cancel", style=ButtonStyle.red)
	async def cancel(self, inter: Interaction, _button: Button) -> None:
		await inter.response.edit_message(content="Shutdown cancelled.", view=None)

		self.stop_shutdown = True
		
		self.stop()


class Developer(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	async def cog_check(self, ctx: Context) -> bool:
		super().cog_check(ctx)

		return await self.bot.is_owner(ctx.author)


	@command(help="Evaluate python code", aliases=['py', 'e'])
	async def eval(self, ctx: Context, mobile_friendly: bool = False, *, code: str):
		output = StringIO()

		injected_print = partial(print, file=output)

		locals_copy = locals().copy()
		locals_copy["print"] = injected_print

		try:
			exec(str(code), None, locals_copy)
		except Exception as error:
			injected_print(''.join(format_exception(error)))

		code_output = output.getvalue()

		if mobile_friendly:
			MAX_LENGTH: int = 4096 - 14

			for i in range(0, len(code_output), MAX_LENGTH):
				output_message = Embed(description=f"```bash\n{code_output[i:i+MAX_LENGTH]}\n```", color=Default.COLOR)
				
				await ctx.message.reply(embed=output_message)
		
		else:
			bytes_message: BytesIO = BytesIO(code_output.encode())
			message_file = File(bytes_message, filename="output")

			await ctx.message.reply(file=message_file)

	
	@command(help="Shutdown the bot", aliases=['s'])
	async def shutdown(self, ctx: Context, force: bool = False) -> None:
		if force:
			await ctx.send(":white_check_mark: Shutting down!")

			await self.bot.close()

			return

		view = shutdownView(ctx.author)

		base_message = await ctx.send(":warning: Shutting down in 60...", view=view)

		await view.wait()

		if not view.stop_shutdown:
			log("status", f"shutting down by shutdown command. (admin: {ctx.author} [{ctx.author.id}])")
			
			await base_message.edit(content=":white_check_mark: Shutting down!", view=None)

			await self.bot.close()


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