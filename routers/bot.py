from fastapi import FastAPI, APIRouter
from discord.ext import commands
from pydantic import BaseModel


class BotStatus(BaseModel):
    status: str


class API_Router:
    def __init__(self, app: FastAPI, bot: commands.Bot):
        self.app = app
        self.router = APIRouter()
        self.bot = bot
        self.register_routes()

    def register_routes(self):

        self.router.get("/bot-status", response_model=BotStatus)(self.get_bot_status)
        self.app.include_router(self.router)

    def get_bot_status(self) -> BotStatus:
        status = "Online" if self.bot.is_ready() else "Offline"
        return BotStatus(status=status)
