import logging
from discord.ext import commands
from utils.embed import Embed
from utils.reaction import Reaction


class Logger:
    def __init__(self):
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.INFO)
        self.embed = Embed()
        self.reaction = Reaction()

    async def info(self, ctx: commands.Context = None, message: str = ""):
        self.logger.info(message)
        if ctx is not None:
            embed = self.embed.create_embed(message, title="Info", color="info")
            await ctx.send(embed=embed)

    async def error(self, ctx: commands.Context = None, message: str = ""):
        self.logger.error(message)
        if ctx is not None:
            embed = self.embed.create_embed(
                f"{self.reaction.red_tick} {message}",
                title="Error",
                color="fail",
            )
            await ctx.send(embed=embed)

    async def log(self, ctx: commands.Context = None, message: str = ""):
        self.logger.info(message)
        if ctx is not None:
            embed = self.embed.create_embed(message, title="Log", color="pass")
            await ctx.send(embed=embed)
