from managers.database import Database


class Checks:
    async def get_user_blacklist(user_id: int):
        db = Database()
        docs = await db.get_user(user_id=user_id).get("blacklist", [])
        return docs

    async def get_guild_blacklist(guild_id: int):
        db = Database()
        docs = await db.get_guild(guild_id=guild_id).get("blacklist", [])
        return docs

    async def allowed_command(ctx) -> bool:
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        guild_blacklist = await Checks.get_guild_blacklist(guild_id)
        user_blacklist = await Checks.get_user_blacklist(user_id)
        print(f"Guild Blacklist: {guild_blacklist}, User Blacklist: {user_blacklist}")
        return (
            ctx.command.name not in guild_blacklist
            and ctx.command.name not in user_blacklist
        )
