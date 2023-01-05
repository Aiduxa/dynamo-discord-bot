# not 100% working

from discord.ext.commands import GroupCog, Bot
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
		if self.page_index > 0:
			self.previous.disabled = False

		if self.page_index < len(self.pages):
			self.next.disabled = False

		return self.author.id == inter.user.id

	
	@button(label="Previous", style=ButtonStyle.blurple, disabled=True)
	async def previous(self, inter: Interaction, button: Button) -> None:
		self.page_index -= 1

		if self.page_index == 0:
			button.disabled = True

		for child in self.children:
			child.options = self.pages_options[self.page_index]

		await inter.response.edit_message(embed=self.pages[self.page_index], view=self, ephemeral=True)

	
	@button(label="Next", style=ButtonStyle.blurple)
	async def next(self, inter: Interaction, button: Button) -> None:
		self.page_index += 1

		if self.page_index == len(self.pages):
			button.disabled = True

		for child in self.children:
			child.options = self.pages_options[self.page_index]

		await inter.response.edit_message(embed=self.pages[self.page_index], view=self, ephemeral=True)




class BuySelect(Select):
	def __init__(self, options: list[SelectOption]) -> None:
		super().__init__(placeholder="Buy", options=options, min_values=1, max_values=5, row=4)

	async def callback(self, inter: Interaction) -> None:
		await inter.response.send_message(self.values, ephemeral=True)


class Buy(GroupCog, name="buy"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="Buy members from other servers")
	@guilds(Default.SERVER)
	async def members(self, inter: Interaction) -> None:
		pages: list[Embed] = []
		pages_options: list[list[SelectOption]] = []

		current_embed = Embed(title="Buy", color=Default.COLOR)
		current_embed.set_footer(text=Default.FOOTER)

		current_options: list[SelectOption] = []
		for index, guild in enumerate(self.bot.guilds):
			if ((index + 1) % 5) == 0:
				pages.append(current_embed)
				pages_options.append(current_options)

				current_embed.clear_fields()
				pages_options.clear()

			current_embed.add_field(name=f"{guild.name} (:zap: `{randint(1,100000)}`)", value=f":gem: **Price:** `{randint(1,10000)}`", inline=False)
			current_options.append(SelectOption(label=guild.name, value=guild.id))

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
	await bot.add_cog(Buy(bot), guilds=[Default.SERVER])