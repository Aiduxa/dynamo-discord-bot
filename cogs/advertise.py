# not 100% working

from discord.ext.commands import Cog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Member, ButtonStyle, SelectOption
from discord.ui import View, button, Button, Select

from random import randint

from utils import Default, log


class BaseView(View):
	def __init__(self, author: Member, pages: list[Embed], pages_options: list[list[SelectOption]]) -> None:
		self.author = author
		self.pages = pages
		self.pages_options = pages_options
		self.page_index: int = 0

		super().__init__(timeout=300.0)

	async def interaction_check(self, inter: Interaction) -> bool:
		return self.author.id == inter.user.id

	
	@button(label="Previous", style=ButtonStyle.blurple, disabled=True)
	async def previous(self, inter: Interaction, button: Button) -> None:
		self.page_index -= 1

		button.disabled = (self.page_index <= 0)
		self.next.disabled = not (self.page_index < len(self.pages) - 1)

		for child in self.children:
			if type(child) == Select:
				try:
					child.options = self.pages_options[self.page_index]
				except IndexError:
					pass

		await inter.response.edit_message(embed=self.pages[self.page_index], view=self)

	
	@button(label="Next", style=ButtonStyle.blurple)
	async def next(self, inter: Interaction, button: Button) -> None:
		self.page_index += 1

		button.disabled = (self.page_index >= len(self.pages) - 1)
		self.previous.disabled = not (self.page_index > 0)

		for child in self.children:
			if type(child) == Select:
				try:
					child.options = self.pages_options[self.page_index]
				except IndexError:
					pass

		await inter.response.edit_message(embed=self.pages[self.page_index], view=self)




class BuySelect(Select):
	def __init__(self, options: list[SelectOption]) -> None:
		super().__init__(placeholder="Buy", options=options, min_values=1, max_values=5, row=4)

	async def callback(self, inter: Interaction) -> None:
		await inter.response.send_message(self.values, ephemeral=True)


class Advertise(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="Advertise in other servers")
	@guilds(Default.SERVER)
	async def advertise(self, inter: Interaction) -> None:
		pages: list[Embed] = []
		pages_options: list[list[SelectOption]] = []

		base_embed: dict = {
			"title": "Advertise",
			"color": Default.COLOR,
			"footer": {"text": Default.FOOTER}
		}

		current_embed = Embed.from_dict(base_embed)

		current_options: list[SelectOption] = []
		for index, guild in enumerate(self.bot.guilds):
			current_embed.add_field(name=f"{guild.name} (:zap: `{randint(1,100000)}`)", value=f":gem: **Price:** `{randint(1,10000)}`", inline=False)
			current_options.append(SelectOption(label=guild.name, value=guild.id))

			if ((index + 1) % 5) == 0:
				pages.append(current_embed)
				current_embed = Embed.from_dict(base_embed)

				if (index + 5) <= len(self.bot.guilds):
					pages_options.append(current_options)
					current_options.clear()

		if len(current_embed.fields) >= 1:
			pages.append(current_embed)
			pages_options.append(current_options)

		view = BaseView(inter.user, pages, pages_options)

		if len(pages) == 1:
			view.next.disabled = True

		view.add_item(BuySelect(pages_options[0]))

		await inter.response.send_message(embed=pages[0], view=view, ephemeral=True)

		await view.wait()


async def setup(bot: Bot) -> None:
	await bot.add_cog(Advertise(bot))