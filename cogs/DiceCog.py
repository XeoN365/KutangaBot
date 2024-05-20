import discord
from discord.ext import commands
from discord import app_commands
import random


class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll_dice", description="Rolls a dice")
    @app_commands.describe(
        dices="Number of dice to roll", sides="Number of sides on the dice"
    )
    async def roll_dice(
        self,
        interaction: discord.Interaction,
        dices: int = 1,
        sides: int = 6,
    ):
        dice_rolls = []
        dice_rolls_ints = []
        for roll in range(int(dices)):
            result = random.randint(1, int(sides))
            dice_rolls.append(str(result))
            dice_rolls_ints.append(result)

        embed = discord.Embed(
            title="Dice rolls:",
            description=" ".join(dice_rolls),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Total: ", value=sum(dice_rolls_ints))
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(DiceCog(bot))
