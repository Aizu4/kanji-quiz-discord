import asyncio

from discord.ext import commands


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        """
        Prints the bot's latency (in milliseconds)
        """
        await ctx.send(f"{self.bot.latency * 1000 :.0f} ms")

    @commands.command(name='report')
    async def report(self, _, *msg: str):
        """
        Send a feedback message to the bot's owner
        """
        await (await self.bot.fetch_user(self.bot.owner_id)).send(' '.join(msg))

    @commands.command(name='kill', hidden=True)
    @commands.is_owner()
    async def kill(self, ctx: commands.Context):
        await ctx.send("Goodbye!")
        await self.bot.close()

    @commands.command(name='echo', hidden=True)
    @commands.is_owner()
    async def echo(self, ctx: commands.Context, *msg: str):
        asyncio.create_task(ctx.message.delete())
        await ctx.send(" ".join(msg))
