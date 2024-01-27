from discord.ext import commands

from services import quiz_service


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start')
    async def start_quiz(self, ctx: commands.Context, *params: str):
        """
        Starts a new game of guessing the readings of kanji
        """
        await quiz_service.start(ctx, *params)

    @commands.command(name='stop')
    async def stop_quiz(self, ctx: commands.Context):
        """
        Stops an ongoing game in the channel
        """
        await quiz_service.stop(ctx)

