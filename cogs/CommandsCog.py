from discord.ext import commands
import discord

from managers.logging import Logger
from managers.database import Database


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = self.bot.logger
        self.guilds: Database = self.bot.db["Guilds"]
        self.users: Database = self.bot.db["Users"]

    async def fetch_user_command_blacklist(self, user_id: int):
        docs = await self.users.find_one({"user_id": user_id})
        if docs:
            return docs.get("command_blacklist", [])
        return []

    async def fetch_guild_command_blacklist(self, guild_id: int):
        docs = await self.guilds.find_one({"guild_id": guild_id})
        if docs:
            return docs.get("command_blacklist", [])
        return []

    @commands.command(name="blacklist")
    @commands.is_owner()
    async def blacklist_command(
        self,
        ctx: commands.Context,
        command: str,
        user: discord.User = None,
        guild: discord.Guild = None,
    ):
        """Blacklists a command for a user or a guild."""
        if user:
            user_id = user.id
            command_blacklist = await self.fetch_user_command_blacklist(user_id)
            if command in command_blacklist:
                await ctx.send(f"{command} is already blacklisted for {user.name}.")
                return
            command_blacklist.append(command)
            await self.users.update_one(
                {"user_id": user_id}, {"$set": {"command_blacklist": command_blacklist}}
            )
            await ctx.send(f"{command} has been blacklisted for {user.name}.")
        elif guild:
            guild_id = guild.id
            guild_command_blacklist = await self.fetch_guild_command_blacklist(guild_id)
            if command in guild_command_blacklist:
                await ctx.send(f"{command} is already blacklisted in {guild.name}")
                return
            guild_command_blacklist.append(command)
            await self.guilds.update_one(
                {"guild_id": guild_id},
                {"$set": {"command_blacklist": guild_command_blacklist}},
            )
            await ctx.send(f"{command} has been blacklisted in {guild.name}.")

    @commands.command(name="unblacklist")
    @commands.is_owner()
    async def unblacklist_command(
        self,
        ctx: commands.Context,
        command: str,
        user: discord.User = None,
        guild: discord.Guild = None,
    ):
        """Unblacklists a command for a user or a guild."""
        if user:
            user_id = user.id
            command_blacklist = await self.fetch_user_command_blacklist(user_id)
            if command not in command_blacklist:
                await ctx.send(f"{command} is not blacklisted for {user.name}.")
                return
            command_blacklist.remove(command)
            await self.users.update_one(
                {"user_id": user_id}, {"$set": {"command_blacklist": command_blacklist}}
            )
            await ctx.send(f"{command} has been unblacklisted for {user.name}.")
        elif guild:
            guild_id = guild.id
            guild_command_blacklist = await self.fetch_guild_command_blacklist(guild_id)
            if command not in guild_command_blacklist:
                await ctx.send(f"{command} is not blacklisted in {guild.name}.")
                return
            guild_command_blacklist.remove(command)
            await self.guilds.update_one(
                {"guild_id": guild_id},
                {"$set": {"command_blacklist": guild_command_blacklist}},
            )
            await ctx.send(f"{command} has been unblacklisted in {guild.name}.")


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
