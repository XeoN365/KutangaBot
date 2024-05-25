from fastapi import FastAPI, APIRouter
from discord.ext import commands
from pydantic import BaseModel


class BotStatus(BaseModel):
    status: str


class BotCogs(BaseModel):
    cogs: list


class BotInfo(BaseModel):
    name: str
    description: str
    cogs: BotCogs
    prefix: str


class API_Router:
    def __init__(self, app: FastAPI, bot: commands.Bot):
        self.app = app
        self.router = APIRouter()
        self.bot = bot
        self.register_routes()

    def register_routes(self):

        self.router.get("/bot-status", response_model=BotStatus)(self.get_bot_status)
        self.router.get("/bot-cogs", response_model=BotCogs)(self.get_bot_cogs)
        self.router.get("/bot-info", response_model=BotInfo)(self.get_bot_info)
        self.app.include_router(self.router)

    def get_bot_status(self) -> BotStatus:
        status = "Online" if self.bot.is_ready() else "Offline"
        return BotStatus(status=status)

    def get_bot_cogs(self) -> BotCogs:
        cogs = [x for x in self.bot.cogs.keys()]
        return BotCogs(cogs=cogs)

    def get_bot_info(self) -> BotInfo:
        return BotInfo(
            name=self.bot.user.name,
            description=self.bot.description,
            cogs=self.get_bot_cogs(),
            prefix=self.bot.command_prefix,
        )
