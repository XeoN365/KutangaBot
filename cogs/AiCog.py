from discord.ext import commands
import discord

from typing import List

from langchain_community.chat_models.ollama import ChatOllama

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables.history import RunnableWithMessageHistory

from utils.embed import Embed
from utils.reaction import Reaction

from datetime import datetime

import math


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory chat history implementation"""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


class AiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.llm = ChatOllama()
        self.store = {}
        self.embed = Embed()
        self.reaction = Reaction()
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    You are an discord AI assistant. 
                    You will help users to the best of your ability with any question they may have. 
                    Make sure to format your answers discord friendly. 
                    Current date is {datetime.now().strftime('%d/%m/%Y')}.
                    """,
                ),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{question}"),
            ]
        )

    def get_session_history(self, user_id: int) -> BaseChatMessageHistory:
        if user_id not in self.store:
            self.store[user_id] = InMemoryHistory()
        return self.store[user_id]

    async def get_response(self, user_id: int, prompt: str):

        chain = self.prompt | ChatOllama(model="llama3.1")

        runner = RunnableWithMessageHistory(
            chain,  # type: ignore
            get_session_history=self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        result = await runner.ainvoke(
            {"question": prompt}, config={"configurable": {"session_id": user_id}}
        )
        return result

    @commands.command()
    async def ask(self, ctx: commands.Context, *, question: str):
        """Ask a question to the LLM."""
        response = await self.get_response(ctx.author.id, question)
        pages = math.ceil(len(response.content) / 1024)
        if pages == 1:
            await ctx.send(response.content, ephemeral=True)
        else:
            for i in range(pages):
                await ctx.send(
                    response.content[i * 1024 : (i + 1) * 1024], ephemeral=True
                )

    @commands.command()
    async def clear_history(self, ctx):
        """Clear the chat history for the current user."""
        if ctx.author.id in self.store:
            del self.store[ctx.author.id]
            await ctx.send("Chat history cleared.")
        else:
            await ctx.send("No chat history found for this user.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if self.bot.user.mentioned_in(message):  # type: ignore
            content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()  # type: ignore
            ctx = await self.bot.get_context(message)
            await self.reaction.add_reaction(ctx, "thinking")
            await self.ask(ctx, question=content)


async def setup(bot: commands.Bot):
    await bot.add_cog(AiCog(bot))
