from discord.ext import commands
import discord
import uuid
from managers.cah_loader import CardAgainstHumanity


class CahCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.logger
        self.current_game = None
        self.cah_manager = CardAgainstHumanity()

    @commands.group()
    async def cah(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command. Use `cah help` for more information.")

    @cah.command()
    async def start(self, ctx, pack_name: str = ""):
        """Starts a new game of Cards Against Humanity"""
        if self.current_game:
            await ctx.send("A game is already in progress.")
            return
        if pack_name == "":
            # Create pagination of packs, use discord.views to display 10 at the time and allow navigation using discord.ui.buttons
            packs = self.cah_manager.get_packs()
            pack_embeds = [
                self.cah_manager.create_pack_embed(pack_name) for pack_name in packs
            ]

    @cah.command()
    async def draw(self, ctx):
        """Draws a card from the deck"""
        # TODO: Draw a card from the deck and send it to the player

    @cah.command()
    async def join(self, ctx):
        """Joins a game of Cards Against Humanity"""
        # TODO: Add the player to the game if there is a game in progress
