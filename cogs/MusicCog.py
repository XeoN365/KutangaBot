import discord
from discord.ext import commands
import wavelink
from typing import Optional, cast
from managers.logging import Logger
from utils.embed import Embed
import datetime
from utils.reaction import Reaction


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = Logger()
        self.embed = Embed()
        self.reaction = Reaction()
        self.timeout = 30
        self.autoplay = wavelink.AutoPlayMode.partial

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
            f"The player has been inactive for {self.timeout} seconds. Goodbye!",
            "Music Player",
        )
        await player.home.send(embed=embed)
        await player.disconnect()

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        queue: wavelink.Queue = player.queue or player.auto_queue
        if not queue:
            return
        songs = ""
        time = 0
        for id, track in enumerate(queue):
            if id < 10:
                hours, reminders = divmod(track.length / 1000, 3600)
                minutes, seconds = divmod(reminders, 60)
                title = (
                    track.title if len(track.title) < 30 else f"{track.title[:30]}..."
                )
                songs += f"{id+1}. **{title}** by **'{track.author}'** {int(minutes)}:{int(seconds)}\n"
            time += track.length
        embed = self.embed.create_embed(songs, "Queue")
        hours, reminders = divmod(time / 1000, 3600)
        minutes, seconds = divmod(reminders, 60)
        text = ""
        if int(hours) > 0:
            if int(hours) < 10:
                text += f"0{int(hours)}:"
        if int(minutes) > 0:
            if int(minutes) < 10:
                text += f"0{int(minutes)}:"
        text += f"{int(seconds)}"

        embed.set_footer(text=f"Total: {len(queue)} | Total play time: {text}")
        await ctx.send(embed=embed)

    @commands.command()
    async def repeat(self, ctx: commands.Context, mode: str):
        if mode.lower() not in ("song", "queue", "off"):
            await self.logger.error(
                ctx,
                message=f"{ctx.author.mention} Repeat mode must be song, queue or off!",
            )
            return
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        queue: wavelink.Queue = player.queue or player.auto_queue
        if not queue:
            return
        print(mode)
        if mode.lower() == "song":
            queue.mode = wavelink.QueueMode.loop
            embed = self.embed.create_embed("Repeat mode is now song!", "Music Player")
            await ctx.send(embed=embed)
        elif mode.lower() == "queue":
            queue.mode = wavelink.QueueMode.loop_all
            embed = self.embed.create_embed("Repeat mode is now queue!", "Music Player")
            await ctx.send(embed=embed)
        elif mode.lower() == "off":
            queue.mode = wavelink.QueueMode.normal
            embed = self.embed.create_embed("Repeat mode is now off!", "Music Player")
            await ctx.send(embed=embed)

    @commands.command(name="autoplay")
    async def autoplay(self, ctx: commands.Context, mode: str):
        if not ctx.guild:
            return
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        if mode.lower() == "on":
            self.autoplay = wavelink.AutoPlayMode.enabled
            embed = self.embed.create_embed("Autoplay is now on!", "Music Player")
            await ctx.send(embed=embed)
        elif mode.lower() == "off":
            self.autoplay = wavelink.AutoPlayMode.partial
            embed = self.embed.create_embed("Autoplay is now off!", "Music Player")
            await ctx.send(embed=embed)
        else:
            await self.logger.error(
                ctx, message=f"{ctx.author.mention} Autoplay must be on or off!"
            )
        player.autoplay = self.autoplay

    @commands.command(name="shuffle")
    async def shuffle(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        queue: wavelink.Queue = player.queue or player.auto_queue
        if not queue:
            return
        queue.shuffle()
        embed = self.embed.create_embed("Queue has been shuffled!", "Music Player")
        await ctx.send(embed=embed)

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: str):
        if not ctx.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        if not player:
            try:
                channel = ctx.author.voice.channel
                player = await channel.connect(cls=wavelink.Player)
            except discord.ClientException:
                await self.logger.error(
                    ctx, message="Failed to connect to voice channel"
                )
                return
            except AttributeError:
                await self.logger.error(
                    ctx, message="Join a voice channel first before using this command!"
                )
                return

        player.inactive_timeout = self.timeout
        player.autoplay = self.autoplay

        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await self.logger.info(
                ctx,
                f"You can only play songs in {player.home.mention}, as the player has already started there!",
            )
            return
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await self.logger.error(
                ctx, message=f"{ctx.author.mention} No results found for {query}"
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            embed = self.embed.create_embed(
                f"Added the playlist **{tracks.name}** ({added} songs) to the queue",
                "Music Player",
                color="pass",
            )
            await ctx.send(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            embed = self.embed.create_embed(
                f"Added **{track}** to the queue", "Music Player", color="pass"
            )
            await ctx.send(embed=embed)

        if not player.playing:
            await player.play(player.queue.get(), volume=5)

    @commands.command(name="skip")
    async def skip(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.skip(force=True)
        await self.reaction.add_reaction(ctx, self.reaction.green_tick)

    @commands.command(name="toggle", aliases=["pause", "resume"])
    async def pause_resume(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.pause(not player.paused)
        embed = self.embed.create_embed(
            f"The song has been {'Paused' if player.paused else 'Resumed'}",
            "Music Player",
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int = 0):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        if volume == 0 or volume == player.volume:
            embed = self.embed.create_embed(
                f"Volume is currently set to **{player.volume}**",
                "Music Player",
            )
            await ctx.send(embed=embed)
        else:
            await player.set_volume(volume)
            embed = self.embed.create_embed(
                f"Volume set to **{volume}**", "Music Player"
            )
            await ctx.send(embed=embed)

    @commands.command(aliases=["dc"])
    async def stop(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        await player.disconnect()

    @commands.group(invoke_without_command=True)
    async def filters(self, ctx: commands.Context):
        """Set filters"""
        available_filters: str = "Currently available filters: \n"
        for command in self.bot.get_cog("MusicCog").walk_commands():
            if command.parent is not None and command.hidden is not True:
                available_filters += f"**{command.name}** - {command.description}\n"
        embed = self.embed.create_embed(available_filters, "Music Player")
        await ctx.send(embed=embed)

    @filters.command(description="Set custom filter")
    async def custom(self, ctx: commands.Context, *, attr: str):
        """Custom filter"""
        filters_raw = attr.split(" ")
        all_filters = {}
        applied_filters: str = ""
        for filter in filters_raw:
            temp = filter.split(":")
            all_filters[temp[0]] = float(temp[1])

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        filters: wavelink.Filters = player.filters
        if "pitch" in all_filters.keys():
            filters.timescale.set(
                pitch=all_filters["pitch"],
            )
            applied_filters += f"Pitch: {all_filters['pitch']}\n"
        if "speed" in all_filters.keys():
            filters.timescale.set(
                speed=all_filters["speed"],
            )
            applied_filters += f"Speed: {all_filters['speed']}\n"
        if "rate" in all_filters.keys():
            filters.timescale.set(
                rate=all_filters["rate"],
            )
            applied_filters += f"Rate: {all_filters['rate']}\n"
        await player.set_filters(filters)
        embed = self.embed.create_embed(
            f"Custom filter enabled!\n{applied_filters}",
            "Music Player",
        )
        await ctx.send(embed=embed)

    @filters.command(description="Nightcore filter")
    async def nightcore(self, ctx: commands.Context):
        """Nightcore filter"""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1.0)
        await player.set_filters(filters)
        embed = self.embed.create_embed(
            "Nightcore enabled!",
            "Music Player",
        )
        await ctx.send(embed=embed)

    @filters.command(description="Vaporwave filter")
    async def vaporwave(self, ctx: commands.Context):
        """Vaporwave filter"""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.0, speed=1.2, rate=0.8)
        await player.set_filters(filters)
        embed = self.embed.create_embed(
            "Vaporwave enabled!",
            "Music Player",
        )
        await ctx.send(embed=embed)

    @filters.command(hidden=True, description="Karaoke filter")
    async def karaoke(self, ctx: commands.Context):
        """Karaoke filter"""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        filters: wavelink.Filters = player.filters
        filters.karaoke.set(level=0.9, mono_level=0.9)
        await player.set_filters(filters)
        embed = self.embed.create_embed(
            "Karaoke enabled!",
            "Music Player",
        )
        await ctx.send(embed=embed)

    @filters.command(description="Clears all filters")
    async def clear(self, ctx: commands.Context):
        """Clears all filters"""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        filters: wavelink.Filters = player.filters
        filters.reset()
        await player.set_filters(filters)
        embed = self.embed.create_embed(
            "Filters cleared!",
            "Music Player",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
