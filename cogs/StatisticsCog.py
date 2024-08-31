from discord.ext import commands
import discord

from managers.logging import Logger
from managers.database import Database


class StatisticsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger: Logger = self.bot.logger
        self.guilds: Database = self.bot.db["Guilds"]
        self.users: Database = self.bot.db["Users"]

    async def cog_load(self):
        await self.get_guilds()
        await self.get_users()

    async def check_if_guild_exists(self, guild_id: int):
        docs = await self.guilds.find_one({"guild_id": guild_id})
        return docs is not None

    async def check_if_user_exists(self, user_id: int):
        docs = await self.users.find_one({"user_id": user_id})
        return docs is not None

    async def add_guild(self, guild: discord.Guild):
        members = [x.id async for x in guild.fetch_members()]
        channels = [x.name for x in await guild.fetch_channels()]
        roles = [x.name for x in await guild.fetch_roles()]
        emojis = [x.name for x in await guild.fetch_emojis()]
        await self.guilds.insert_one(  # type: ignore
            {
                "guild_id": guild.id,
                "guild_name": guild.name,
                "guild_members": members,
                "guild_channels_count": len(channels),
                "guild_roles_count": len(roles),
                "guild_emojis_count": len(emojis),
                "guild_created_at": guild.created_at,
                "guild_owner_id": guild.owner_id,
                "guild_disabled_commands": [],
            }
        )

    async def add_user(self, user: discord.User):
        await self.users.insert_one(  # type: ignore
            {
                "user_id": user.id,
                "user_name": user.name,
                "user_discriminator": user.discriminator,
                "user_created_at": user.created_at,
                "user_bot": user.bot,
                "blacklist_commands": ["cog", "eval"],
                "blacklist_channels": [],
            }
        )

    async def update_guild(self, guild: discord.Guild):
        await self.guilds.update_one(  # type: ignore
            {"guild_id": guild.id},
            {
                "$set": {
                    "guild_name": guild.name,
                    "guild_members": [x.id async for x in guild.fetch_members()],
                    "guild_channels_count": len(await guild.fetch_channels()),
                    "guild_roles_count": len(await guild.fetch_roles()),
                    "guild_emojis_count": len(await guild.fetch_emojis()),
                }
            },
        )

    async def update_user(self, user: discord.User):
        await self.users.update_one(  # type: ignore
            {"user_id": user.id},
            {
                "$set": {
                    "user_name": user.name,
                    "user_discriminator": user.discriminator,
                    "user_created_at": user.created_at,
                    "user_bot": user.bot,
                }
            },
        )

    async def get_guilds(self):
        async for guild in self.bot.fetch_guilds():
            if await self.check_if_guild_exists(guild.id) == 0:
                await self.add_guild(guild)
            else:
                await self.update_guild(guild)

    async def get_users(self):
        async for guild in self.bot.fetch_guilds():
            async for member in guild.fetch_members():
                if await self.check_if_user_exists(member.id) == 0:
                    await self.add_user(member)
                else:
                    await self.update_user(member)

    @commands.command(name="update-guilds")
    @commands.is_owner()
    async def update_guilds(self, ctx: commands.Context):
        await self.get_guilds()
        await self.logger.info(ctx, "Updated guilds")

    @commands.command(name="update-users")
    @commands.is_owner()
    async def update_users(self, ctx: commands.Context):
        await self.get_users()
        await self.logger.info(ctx, "Updated users")


async def setup(bot):
    await bot.add_cog(StatisticsCog(bot))
