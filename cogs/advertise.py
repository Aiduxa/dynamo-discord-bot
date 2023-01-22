from discord.ext.commands import Cog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Member, ButtonStyle, SelectOption
from discord.ui import View, button, Button, Select

from utils import Default, Emoji, fetch_guild, DBGuildNotFound, fetch_user, update_user_gems, log


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
		await inter.response.send_message(content="Preparing embed, this will take a second...", ephemeral=True)

		pages_list: list[Embed] = []
		pages_options: list[list[SelectOption]] = []

		user_data: dict = await fetch_user(self.bot.POOL, inter.user.id)

		base_embed_data: dict = {
			"title": "Advertise",
			"description": f"{Emoji.CURRENCY} Balance: `{user_data['gems']}`",
			"footer": {
				"text": Default.FOOTER,
				"icon_url": inter.user.avatar.url
			}
		}

		current_page = Embed.from_dict(base_embed_data)
		current_options: list[SelectOption] = []

		for i, guild in enumerate(self.bot.guilds):
			try:
				guild_data: dict = await fetch_guild(self.bot.POOL, guild.id)
			except DBGuildNotFound:
				i -= 1

				continue

			label: str = f"{guild.name} ({Emoji.CURRENCY} `{guild_data['activity_power']}`)"

			guild_users: list = guild_data["guild_users"]

			guild_activity: str = f"{Emoji.SUPER_ACTIVE} `{len(guild_users[0])}` | {Emoji.ACTIVE} `{len(guild_users[1])}` | {Emoji.ONLINE} `{len(guild_users[2])}`"

			current_page.add_field(name=label, value=guild_activity, inline=False)

			current_options.append(SelectOption(label=label, value=str(guild.id)))

			if i % 5 == 0:
				pages_list.append(current_page)
				current_page = Embed.from_dict(base_embed_data)

				pages_options.append(current_options)
				current_options.clear()

		if current_page.fields:
			pages_list.append(current_page)
		if current_options:
			pages_options.append(current_options)

		view = BaseView(inter.user, pages_list, pages_options)
		view.add_item(BuySelect(pages_options[0]))

		await inter.edit_original_response(content="", embed=pages_list[0], view=view)

		await view.wait()



async def setup(bot: Bot) -> None:
	await bot.add_cog(Advertise(bot))