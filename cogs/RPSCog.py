from discord.ext import commands
import discord
from utils.reaction import Reaction


class RPSButtons(discord.ui.View):
    def __init__(self, *, timeout=150):
        super().__init__(timeout=timeout)
        self.choice = 0

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.gray, emoji="👊")
    async def rock(self, interaction: discord.ui.Button, btn: discord.Interaction):
        self.choice = 1
        btn.style = discord.ButtonStyle.green
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="You chose rock!", view=self)
        self.stop()

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.gray, emoji="✋")
    async def paper(self, interaction: discord.ui.Button, btn: discord.Interaction):
        self.choice = 2
        btn.style = discord.ButtonStyle.green
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="You chose paper!", view=self)
        self.stop()

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.gray, emoji="✌️")
    async def scissors(self, interaction: discord.ui.Button, btn: discord.Interaction):
        self.choice = 3
        btn.style = discord.ButtonStyle.green
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="You chose Scissors", view=self)
        self.stop()


class RPSCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = self.bot.logger
        self.reaction = Reaction()

    @commands.command(name="rps", description="Play rock paper scissors")
    async def rps(self, ctx: commands.Context, user: discord.Member):
        """Play rock paper scissors with another user. Usage: rps <user>"""
        if user is not None and user != ctx.author:
            await self.reaction.add_reaction(ctx, "pass")
            await ctx.send(
                f"Rock paper scissors battle between {ctx.author.display_name} and {user.display_name}!"
            )
            p1view = RPSButtons()
            await ctx.author.send(
                f"You're about to play rock paper scissors with {user.display_name}\nChoose your option:",
                view=p1view,
            )
            await p1view.wait()

            p2view = RPSButtons()
            await user.send(
                f"You're about to play rock paper scissors with {ctx.author.display_name}\nChoose your option:",
                view=p2view,
            )
            await p2view.wait()

            if p1view.choice != 0 and p2view.choice != 0:
                choices = {
                    1: "👊 Rock",
                    2: "✋ Paper",
                    3: "✌️ Scissors",
                }
                embed = discord.Embed(title="Rock Paper Scissors", color=0x7500EB)
                embed.add_field(
                    name=f"{ctx.author.display_name} choice",
                    value=choices[p1view.choice],
                    inline=True,
                )
                embed.add_field(
                    name=f"{user.display_name} choice",
                    value=choices[p2view.choice],
                    inline=True,
                )
                msg = ""
                result = (p1view.choice - p2view.choice) % 3
                if result == 0:
                    msg = f"{ctx.author.display_name} and {user.display_name} tied!"
                elif result == 1:
                    msg = f"{ctx.author.mention}👑 won with {choices[p1view.choice]}!"
                elif result == 2:
                    msg = f"{user.mention}👑 won with {choices[p2view.choice]}!"

                await ctx.send(msg, embed=embed)
        else:
            raise commands.BadArgument(
                "You can't play rock paper scissors with yourself!"
            )


async def setup(bot):
    await bot.add_cog(RPSCog(bot))
