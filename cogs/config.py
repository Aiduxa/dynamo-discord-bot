from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, guilds
from discord import Interaction, Embed, Member, ButtonStyle, Attachment, Permissions, PermissionOverwrite, Forbidden, Guild, TextChannel, utils
from discord.ui import View, button, Button

from utils import Default, log, update_guild_adembed, get_guild_adembed, update_guild_invite_url, fetch_guild, create_guild, update_guild_adchannel, DBGuildNotFound


class BaseView(View):
	def __init__(self, author: Member, guild_id: int, bot: Bot, ad_embed: dict) -> None:
		self.author = author
		self.guild_id = guild_id
		self.bot = bot
		self.ad_embed = ad_embed

		super().__init__(timeout=150)

	async def interaction_check(self, inter: Interaction) -> bool:
		return self.author.id == inter.user.id

	
	@button(label="Save", style=ButtonStyle.green)
	async def save(self, inter: Interaction, _button: Button) -> None:
		final_embed = Embed.from_dict(self.ad_embed)

		message: str = ":white_check_mark: Changes saved!"

		try:
			await update_guild_adembed(self.bot.POOL, self.guild_id, self.ad_embed)
		except Exception as e:
			log("error", str(e))

			message = ":warning: Something wen't wrong!"

		await inter.response.edit_message(content=message, embed=final_embed, view=None)

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
	async def ad(self, inter: Interaction, title: str = Default.AD_EMBED_TITLE, description: str = "", color: str = "000000", display_owner: bool = False, display_logo: bool = False, banner: Attachment | None = None) -> None:
		if (title == Default.AD_EMBED_TITLE) and (description == "") and (color == "000000") and (display_owner == False) and (display_logo == False) and (banner == None):
			try:
				ad_embed_data: dict = await get_guild_adembed(self.bot.POOL, int(inter.guild.id))
			except Exception as e:
				log("error", str(e))

				await inter.response.send_message("Your server doesn't have an advertisement yet, try creating one.", ephemeral=True)
			else:
				ad_embed = Embed.from_dict(ad_embed_data)

				await inter.response.send_message(embed=ad_embed, ephemeral=True)

			return

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

		view = BaseView(inter.user, int(inter.guild.id), self.bot, base_embed)

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
				await update_guild_invite_url(self.bot.POOL, int(inter.guild.id), invite)
			except Exception as e:
				log("error", str(e))

				message = ":warning: Something wen't wrong!"

			await inter.response.send_message(message, ephemeral=True)


	@command()
	@guilds(Default.SERVER)
	async def channel(self, inter: Interaction, name: str | None = None) -> None:
		guild: Guild = inter.guild

		try:
			guild_data: dict = await fetch_guild(self.bot.POOL, guild.id)
		except DBGuildNotFound:
			await create_guild(self.bot.POOL, guild.id)
		
		try:
			channel: TextChannel | None = self.bot.get_channel(int(guild_data["ad_channel"]))	
		except:
			channel = None

		if channel != None:
			if name != None:
				await channel.edit(name=name)

				await inter.response.send_message(f"Updated {channel.mention}", ephemeral=True)

			else:
				await inter.response.send_message(f"{channel.mention} already exists.", ephemeral=True)

			return

		permissions = dict(Permissions(view_channel=True))

		overwrites = {guild.default_role: PermissionOverwrite(**permissions)}

		channel_name = name if name != None else Default.CHANNEL

		try:
			channel = await guild.create_text_channel(channel_name, position=0, overwrites=overwrites)

		except Exception as e:
			if type(e) == Forbidden:
				await inter.response.send_message("Missing `Manage Channels` permission.", ephemeral=True)

				return

			await inter.response.send_message("Something went wrong!", ephemeral=True)

			log("error", str(e), True)

		else:
			await inter.response.send_message(f":white_check_mark: Created {channel.mention}.", ephemeral=True)

			await update_guild_adchannel(self.bot.POOL, guild.id, channel.id)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Config(bot), guilds=[Default.SERVER])