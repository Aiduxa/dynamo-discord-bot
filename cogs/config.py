from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Member, ButtonStyle, Attachment
from discord.ui import View, button, Button

from utils import Default


class BaseView(View):
	def __init__(self, author: Member, ad_embed: dict) -> None:
		self.author = author
		self.ad_embed = ad_embed

		super().__init__(timeout=150)

	async def interaction_check(self, inter: Interaction) -> bool:
		return self.author.id == inter.user.id

	
	@button(label="Save", style=ButtonStyle.green)
	async def save(self, inter: Interaction, _button: Button) -> None:
		final_embed = Embed.from_dict(self.ad_embed)

		await inter.response.edit_message(content=":white_check_mark: Changes saved!", embed=final_embed, view=None)

		self.stop()


class Config(GroupCog, name="config"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="Configure your guild's advertisement")
	@guilds(Default.SERVER)
	async def ad(self, inter: Interaction, title: str = "CLICK HRE TO JOIN!", description: str = "", color: str = "000000", display_owner: bool = False, display_logo: bool = False, banner: Attachment | None = None) -> None:
		error_message: str = ""
		
		try:
			int(color.replace('#', ''), 16)
		except Exception:
			error_message += "Invalid `color` value, please provide a valid `hex code`.\n"

		if len(title) > 256:
			error_message += "`title` can't be longer than `256` characters!\n"

		if len(description) > 4096:
			error_message = "`description` can't be longer than `4096` characters!\n"

		if error_message != "":
			await inter.response.send_message(error_message, ephemeral=True)

			return
		
		base_embed: dict = {
			"title": title,
			"description": description,
			"color": int(color.replace('#', ''), 16),
			"footer": {"text": Default.FOOTER},
			"url": "https://google.com"
		}

		if display_owner:
			base_embed["author"] = {
				"name": str(inter.user),
				"icon_url": inter.user.avatar.url,
				"url": f"https://discord.com/users/{inter.user.id}"
			}

		if display_logo:
			base_embed["thumbnail"] = {
				"url": inter.guild.icon.url
			}

		if banner != None:
			base_embed["image"] = {
				"url": banner.url
			}
		
		embed = Embed.from_dict(base_embed)

		view = BaseView(inter.user, base_embed)

		await inter.response.send_message(embed=embed, view=view, ephemeral=True)

		await view.wait()


async def setup(bot: Bot) -> None:
	await bot.add_cog(Config(bot), guilds=[Default.SERVER])