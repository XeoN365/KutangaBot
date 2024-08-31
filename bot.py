import discord
from discord.ext import commands
import os
from managers.database import Database
from managers.logging import Logger
import wavelink
from utils.embed import Embed
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import FastAPI, APIRouter
import uvicorn
import asyncio
from routers.bot import API_Router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


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

    async def fetch_user_command_blacklist(self, user_id: int):
        docs = await self.users.find_one({"user_id": user_id})
        if docs:
            return docs.get("command_blacklist", [])
        return []

    async def fetch_guild_command_blacklist(self, guild_id: int):
        docs = await self.guilds.find_one({"guild_id": guild_id})
        if docs:
            return docs.get("command_blacklist", [])
        return []

    @commands.check
    async def allowed_command(self, ctx):
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        user_blacklist = await self.fetch_user_command_blacklist(user_id)
        guild_blacklist = await self.fetch_guild_command_blacklist(guild_id)
        if ctx.command.name in user_blacklist or ctx.command.name in guild_blacklist:
            return False
        return True

    async def setup_hook(self) -> None:
        await self.load_cogs()
        await self.database.test()
        nodes = [wavelink.Node(uri=os.getenv("LLURL"), password=os.getenv("LLPASS"))]
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=False)

    async def load_cogs(self):
        for cog in self.startup_cogs:
            await self.logger.info(message=f"Loading cog: {cog}")
            await self.load_extension(f"cogs.{cog}")


def main():
    intents = discord.Intents.all()
    bot = KutangaBot(
        intents=intents, command_prefix="n!", application_id=os.getenv("APPLICATION_ID")
    )
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
