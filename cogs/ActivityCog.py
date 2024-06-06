from discord.ext import commands, tasks
import discord
import random


class ActivityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.logger = self.bot.logger
        self.loop = 0
        self.change_status.start()
        self.activities = [
            discord.Activity(type=discord.ActivityType.watching, name="you sleep"),
            discord.Activity(type=discord.ActivityType.listening, name="n!help"),
            discord.Activity(type=discord.ActivityType.streaming, name="with your mom"),
        ]

    @commands.Cog.listener()
    async def on_cog_unload(self):
        await self.change_status.cancel()

    @tasks.loop(seconds=60)
    async def change_status(self):

        self.loop += 1
        if self.loop >= len(self.activities):
            self.loop = 0
        await self.bot.change_presence(activity=self.activities[self.loop])


async def setup(bot):
    await bot.add_cog(ActivityCog(bot))
