from discord.ext import commands
import discord
from utils.reaction import Reaction
import asyncio
import wavelink
from utils.embed import Embed


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.logger
        self.embed = Embed()
        self.reaction = Reaction()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self, payload: wavelink.NodeReadyEventPayload
    ) -> None:
        await self.logger.info(message=f"Wavelink node ready: {payload.node}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: wavelink.TrackStartEventPayload
    ) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        track: wavelink.Playable | None = payload.track

        embed = self.embed.create_embed(
            f"**{track.title}** by '{track.author}'", "Now Playing"
        )
        if track.artwork:
            embed.set_image(url=track.artwork)
        if track.album.name:
            embed.add_field(name="Album", value=track.album.name, inline=False)

        await player.home.send(embed=embed)

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        embed = self.embed.create_embed(
            f"The player has been inactive for {player.inactive_timeout} seconds. Goodbye!",
            "Music Player",
        )
        await player.home.send(embed=embed)
        await player.disconnect()

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
