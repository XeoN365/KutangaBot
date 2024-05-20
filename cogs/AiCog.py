import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import math
import re
from discord.utils import get
from managers.logging import Logger
from utils.reaction import Reaction
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
import os


class AiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.logger: Logger = self.bot.logger
        self.reaction: Reaction = Reaction()
        self.db: AsyncIOMotorDatabase = self.bot.db["AiContext"]

    async def check_for_context(self, userid):
        return await self.db.find_one({"userid": userid})

    async def append_context(self, userid, context):
        date = datetime.now()
        check = await self.check_for_context(userid=userid)
        if check is not None:
            query = {"userid": userid}
            vals = {"$set": {"context": context, "date": date}}
            await self.db.update_one(query, vals)
        else:
            await self.db.insert_one(
                {
                    "userid": userid,
                    "context": context,
                    "date": date,
                }
            )

    @commands.command()
    async def reset_context(self, ctx: commands.Context):
        await self.append_context(userid=ctx.author.id, context=[])
        await ctx.send(f"Context for {ctx.author.display_name} has been reset.")

    @commands.command(name="question", description="Ask a question")
    async def ask_question(self, ctx: commands.Context, *, question: str):
        pattern = re.compile(r"<@[0-9]+>")
        context = list()
        if pattern.search(question):
            user: discord.Member = ctx.guild.get_member(
                int(pattern.search(question).group(0)[2:-1])
            )
            if user is not None:
                question = question.replace(
                    pattern.search(question).group(0), user.name
                )
        query = await self.check_for_context(userid=ctx.author.id)
        if query is not None:
            delta: timedelta = datetime.now() - query["date"]
            if delta.seconds > 600:
                context = []
            else:
                context = query["context"]

        data = {
            "model": "dolphin-llama3",
            "prompt": f"{question}",
            "system": "",
            "stream": False,
            "context": context,
        }
        data = json.dumps(data)
        url = os.getenv("LLM_API_URL")
        response = await make_post_request(url, data)
        pages = math.ceil(len(response["response"]) / 1024)
        if pages == 1:
            await ctx.send(response["response"], ephemeral=True)
        else:
            for i in range(pages):
                await ctx.send(
                    response["response"][i * 1024 : (i + 1) * 1024], ephemeral=True
                )
        await self.append_context(userid=ctx.author.id, context=response["context"])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        elif message.content.startswith(f"<@{self.bot.user.id}>"):
            content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            ctx = await self.bot.get_context(message)
            await self.reaction.add_reaction(ctx, "thinking")
            await self.ask_question(ctx, question=content)


async def make_post_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=data) as response:
            return await response.json()


async def setup(bot):
    await bot.add_cog(AiCog(bot))
