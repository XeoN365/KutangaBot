import discord


class Embed:
    def __init__(self):
        self.colors = {
            "pass": discord.Color.green(),
            "fail": discord.Color.red(),
            "info": discord.Color.blue(),
            "default": discord.Color.blurple(),
        }

    def create_embed(self, description, title="KutangaBot", color="default"):
        embed = discord.Embed(title="", description="", color=self.colors[color])
        embed.add_field(name=title, value=description, inline=False)
        return embed
