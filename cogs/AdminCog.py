from discord.ext import commands
import discord
from async_eval import eval as aeval


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.logger

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, args):
        cmd = args[9:-3]
        try:
            result = await aeval(cmd, {"self": self.bot, "ctx": ctx})
            if result is not None:
                await self.logger.info(ctx, result)
        except Exception as e:
            await self.logger.error(ctx, e)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
