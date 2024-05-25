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

    async def setup_hook(self) -> None:
        await self.load_cogs()
        await self.database.test()
        nodes = [wavelink.Node(uri=os.getenv("LLURL"), password=os.getenv("LLPASS"))]
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=False)

    async def load_cogs(self):
        for cog in self.startup_cogs:
            await self.logger.info(message=f"Loading cog: {cog}")
            await self.load_extension(f"cogs.{cog}")


async def start_fastapi():
    fast_config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    fast_server = uvicorn.Server(fast_config)
    await fast_server.serve()


async def start_bot(bot: KutangaBot):
    await bot.start(os.getenv("TOKEN"))


def setup(app: FastAPI, bot: KutangaBot) -> None:
    router = APIRouter()
    api_router = API_Router(app=app, bot=bot)
    router.include_router(api_router.router)
    app.include_router(router)


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = KutangaBot(
        intents=intents, command_prefix="n!", application_id=os.getenv("APPLICATION_ID")
    )
    setup(app=app, bot=bot)
    bot_task = asyncio.create_task(start_bot(bot=bot))
    fastapi_task = asyncio.create_task(start_fastapi())

    await asyncio.gather(bot_task, fastapi_task)


if __name__ == "__main__":
    asyncio.run(main())
