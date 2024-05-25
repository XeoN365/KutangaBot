from discord.ext import commands, tasks
import discord
import random


class ActivityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.logger = self.bot.logger

    @commands.Cog.listener()
    async def on_cog_load(self):
        await self.change_status.start()

    @commands.Cog.listener()
    async def on_cog_unload(self):
        await self.change_status.cancel()

    @tasks.loop(seconds=10)
    async def change_status(self):

        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"you sleep"),
            discord.Activity(type=discord.ActivityType.listening, name=f"n!help"),
            discord.Activity(type=discord.ActivityType.streaming, name="pornhub"),
        ]
        rnd = random.choice(activities)
        await self.bot.change_presence(activity=rnd)


async def setup(bot):
    await bot.add_cog(ActivityCog(bot))
