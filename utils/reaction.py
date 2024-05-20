from discord.ext import commands


class Reaction:
    def __init__(self):
        self.green_tick = "✅"
        self.red_tick = "❌"
        self.thinking_face = "🤔"

    async def add_reaction(self, ctx: commands.Context, emoji: str):
        if emoji.lower() == "pass":
            await ctx.message.add_reaction(self.green_tick)
        elif emoji.lower() == "fail":
            await ctx.message.add_reaction(self.red_tick)
        elif emoji.lower() == "thinking":
            await ctx.message.add_reaction(self.thinking_face)
