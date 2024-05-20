import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from managers.database import Database
from managers.logging import Logger
import wavelink
from utils.embed import Embed
from motor.motor_asyncio import AsyncIOMotorDatabase

load_dotenv()


class KutangaBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = Logger()
        self.startup_cogs = ["CogManager"]
        self.embed = Embed()
        self.database = Database(self.logger)
        self.db: AsyncIOMotorDatabase = self.database.db

    async def on_ready(self):
        await self.logger.info(message=f"Logged in as: {self.user}")
        await self.logger.info(message=f"Bot ID: {self.user.id}")
        await self.tree.sync()

    async def setup_hook(self) -> None:
        await self.load_cogs()
        await self.database.test()
        nodes = [wavelink.Node(uri=os.getenv("LLURL"), password=os.getenv("LLPASS"))]
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=False)

    async def load_cogs(self):
        for cog in self.startup_cogs:
            await self.logger.info(message=f"Loading cog: {cog}")
            await self.load_extension(f"cogs.{cog}")


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = KutangaBot(
        intents=intents, command_prefix="n!", application_id=os.getenv("APPLICATION_ID")
    )
    bot.run(os.getenv("TOKEN"))
