from discord.ext import commands, tasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime, timedelta
from utils.embed import Embed
import discord


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.embed = Embed()
        self.logger = self.bot.logger
        self.db: AsyncIOMotorDatabase = self.bot.db["reminders"]
        self.remind.start()

    async def _add_reminder(self, userid, date, description):
        query = {
            "userid": userid,
            "date": date,
            "description": description,
        }
        result = await self.db.insert_one(query)
        return result.inserted_id

    async def _remove_reminder(self, userid, date):
        query = {"userid": userid, "date": date}
        res = await self.db.delete_one(query)
        return res.deleted_count

    def _get_reminders(self, userid):
        query = {"userid": userid}
        result = self.db.find(query)
        return result

    @commands.group(
        name="reminders", description="List all reminders", invoke_without_command=True
    )
    async def reminders(self, ctx: commands.Context):
        docs = await self.db.count_documents({"userid": ctx.author.id})
        print(docs)
        if docs == 0:
            await self.logger.error(
                ctx, f"No reminders found for **{ctx.author.display_name}**"
            )
            return

        result = self.db.find({"userid": ctx.author.id})
        embed = self.embed.create_embed(
            f"Reminders for **{ctx.author.display_name}**", "Reminders"
        )
        for reminder in await result.to_list(length=100):
            date = reminder["date"].date()
            time = reminder["date"].time()
            embed.add_field(
                name=f"**{date}** at **{time}**",
                value=reminder["description"],
                inline=False,
            )
        await ctx.send(embed=embed)

    @reminders.command(name="add", description="Add a reminder")
    async def add(
        self, ctx: commands.Context, date: Optional[str], time: str, *, description: str
    ):
        current_date = datetime.today().date()
        if date is not None:
            try:
                prop_date = datetime.strptime(date, "%d/%m/%Y").date()
                if prop_date < current_date:
                    await self.logger.error(ctx, "Date must be in the future")
                    return
                date = prop_date
            except ValueError:
                await self.logger.error(ctx, "Date must be in the format DD/MM/YYYY")
                return
        else:
            date = current_date
        if time is None:
            await self.logger.error(ctx, "Time must be in the format HH:MM:SS")
            return
        time = datetime.strptime(time, "%H:%M").time()
        date = datetime.combine(date=date, time=time)
        check_for_existing = await self.db.count_documents(
            {"userid": ctx.author.id, "date": date}
        )
        if check_for_existing > 0:
            await self.logger.error(ctx, "Reminder already exists")
            return

        result = await self._add_reminder(
            userid=ctx.author.id, date=date, description=description
        )
        if result is not None:
            embed = self.embed.create_embed(
                f"Reminder added for **{date.date()}** at **{time}**", "Reminders"
            )
            await ctx.send(embed=embed)
        else:
            await self.logger.error(
                ctx, f"Error adding reminder for **{ctx.author.display_name}**"
            )

    @reminders.command(name="remove", description="Remove a reminder")
    async def remove(self, ctx: commands.Context, date: str, time: Optional[str]):
        if date == "all" and time is None:
            result = await self.db.delete_many({"userid": ctx.author.id})
            if result.deleted_count > 0:
                embed = self.embed.create_embed(
                    f"All reminders removed for **{ctx.author.display_name}**",
                    "Reminders",
                )
                await ctx.send(embed=embed)
                return
            else:
                await self.logger.error(
                    ctx, f"Error removing all reminders for {ctx.author.display_name}"
                )
                return
        result = self._get_reminders(userid=ctx.author.id)
        if result is None:
            embed = self.embed.create_embed(
                f"No reminders found for **{ctx.author.display_name}**", "Reminders"
            )
            await ctx.send(embed=embed)
            return
        time = datetime.strptime(time, "%H:%M").time()
        _date = datetime.strptime(date, "%d/%m/%Y").date()
        val = datetime.combine(date=_date, time=time)
        result = await self._remove_reminder(userid=ctx.author.id, date=val)
        if result > 0:
            embed = self.embed.create_embed(
                f"Reminder removed for **{date} {time}**", "Reminders"
            )
            await ctx.send(embed=embed)
            return
        else:
            await self.logger.error(
                ctx, f"Error removing reminder for **{date} {time}**"
            )
            return

    def cog_unload(self):
        self.remind.cancel()

    @tasks.loop(seconds=30.0)
    async def remind(self):
        collections = self.db.find({})
        for reminder in await collections.to_list(length=100):
            _date = datetime.now().date()
            time = datetime.now().time().replace(second=0, microsecond=0)
            date = datetime.combine(date=_date, time=time)
            if reminder["date"] <= date:
                embed = self.embed.create_embed(
                    f"Reminder for **{reminder['description']}**", "Reminders"
                )
                user = await self.bot.fetch_user(reminder["userid"])
                if user is not None:
                    await user.send(embed=embed)
                else:
                    await self.logger.error(
                        message=f"Error sending reminder for **{user}**"
                    )
                    return
                await self._remove_reminder(
                    userid=reminder["userid"], date=reminder["date"]
                )


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))
