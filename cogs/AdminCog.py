from discord.ext import commands
from async_eval import eval as aeval
from managers.logging import Logger


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger: Logger = self.bot.logger

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
