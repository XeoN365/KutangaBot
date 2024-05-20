from discord.ext import commands
import discord
from utils.reaction import Reaction
import asyncio


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.logger
        self.reaction = Reaction()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        await self.logger.error(ctx=ctx, message=error)
        await asyncio.sleep(1)
        await ctx.message.clear_reactions()
        await self.reaction.add_reaction(ctx, "fail")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        await asyncio.sleep(1)
        await ctx.message.clear_reactions()
        await self.reaction.add_reaction(ctx, "thinking")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        await asyncio.sleep(1)
        await ctx.message.clear_reactions()
        await self.reaction.add_reaction(ctx, "pass")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        pass

    @commands.Cog.listener()
    async def on_guild_update(self, guild: discord.Guild):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        pass

    @commands.Cog.listener()
    async def on_memeber_ban(self, guild: discord.Guild, user: discord.Member):
        pass


async def setup(bot):
    await bot.add_cog(EventsCog(bot))
