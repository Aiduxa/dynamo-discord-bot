from os import getenv
from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
load_dotenv()



class Bot(Bot):
    def __init__(self) -> None:
        super().__init__(
            application_id=getenv("application_id"),
            intents=Intents.default()
        )

    async def on_ready(self) -> None:
        print("running")

    async def setup_hook(self) -> None:
        # this basically handles everything that needs to be done before the bot is ran. Typically u'd load ur cogs here and sync your app commands (slash commands). Maybe start a discord.ext.tasts.Loop aswell
        pass

if __name__ == '__main__':
    Bot().run(getenv("token"))