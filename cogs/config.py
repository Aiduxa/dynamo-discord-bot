from discord.ext.commands import GroupCog, Bot, Context
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Member, ButtonStyle, Attachment, Permissions
from discord.ui import View, button, Button
from asyncpg.pool import Pool

from utils import Default, log, database


class BaseView(View):
	def __init__(self, author: Member, ad_embed: dict, pool: Pool) -> None:
		self.author = author
		self.guild_id = guild_id
		self.bot = bot
		self.ad_embed = ad_embed
		self.POOL = pool

		super().__init__(timeout=150)

	async def interaction_check(self, inter: Interaction) -> bool:
		return self.author.id == inter.user.id

	
	@button(label="Save", style=ButtonStyle.green)
	async def save(self, inter: Interaction, _button: Button) -> None:
		final_embed = Embed.from_dict(self.ad_embed)

		if self.ad_embed.get("author"):
			self.ad_embed["author"] = "true"
		if self.ad_embed.get("thumbnail"):
			self.ad_embed["thumbnail"] = "true"
		if self.ad_embed.get("banner"):
			self.ad_embed["banner"] = self.ad_embed["banner"]["url"]

		await database.update_adembed(self.POOL, inter.guild_id, self.ad_embed)

		await inter.response.edit_message(content=":white_check_mark: Changes saved!", embed=final_embed, view=None)

		self.stop()


class Config(GroupCog, name="config"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	async def interaction_check(self, inter: Interaction) -> bool:
		perms: Permissions = inter.user.guild_permissions

		return perms.administrator or perms.manage_guild or (inter.user.id == inter.guild.owner_id)


	@command(description="Configure your guild's advertisement")
	@guilds(Default.SERVER)
	async def ad(self, inter: Interaction, title: str = "CLICK HERE TO JOIN!", description: str = None, color: str = "000000", display_owner: bool = False, display_logo: bool = False, banner: Attachment | None = None) -> None:
		error_message: str = ""
		
		try:
			int(color.replace('#', ''), 16)
		except Exception:
			error_message += "Invalid `color` value, please provide a valid `hex code`.\n"

		if title and len(title) > 256:
			error_message += "`title` can't be longer than `256` characters!\n"

		if description and len(description) > 4096:
			error_message = "`description` can't be longer than `4096` characters!\n"

		if error_message != "":
			await inter.response.send_message(error_message, ephemeral=True)

			return
		
		base_embed: dict = {
			"title": title,
			"description": description,
			"color": int(color.replace('#', ''), 16),
			"footer": {"text": Default.FOOTER}
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

		view = BaseView(inter.user, base_embed, self.bot.POOL)

		await inter.response.send_message(embed=embed, view=view, ephemeral=True)

		await view.wait()


	@command(description="Configure your guild's invite link")
	@guilds(Default.SERVER)
	async def invite(self, inter: Interaction, invite: str) -> None:
		if not invite.startswith("https://discord.gg/"):
			await inter.response.send_message("Invalid invitation link!", ephemeral=True)

		else:
			message: str = ":white_check_mark: Saved new invitation link."

			try:
				await update_custom_invite_url(self.bot.POOL, int(inter.guild.id), invite)
			except Exception as e:
				log("error", str(e))

				message = ":warning: Something wen't wrong!"

		await database.update_guild_invite_url(self.bot.POOL, inter.guild_id, invite)

		await inter.response.send_message(":white_check_mark: Saved new invitation link.", ephemeral=True)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Config(bot), guilds=[Default.SERVER])