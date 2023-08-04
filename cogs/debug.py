import asyncio

import discord
from discord.ext import commands

import datetime
from random import choice


def get_status():
    while True:
        yield "nyan"; yield "buu"


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(f"`{error}`")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == 966274142229913631:
            return
        if isinstance(message.channel, discord.channel.DMChannel):
            print(message.author, message.content)
            await message.channel.send(
                choice([
                    'ok', 'lol', 'xd', 'spoko', 'dobrze', 'mhm', 'k', 'xdd'
                ])
            )
        elif ":murk:" in message.content:
            await message.channel.send("<:murk:989593406609190952>")
        elif "rav idź spać" in message.content:
            await message.channel.send("rav nie idź spać")
        elif "co" == message.content.lower():
            await message.channel.send("jajco")

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        """
        Prints the bot's latency (in milliseconds)
        """
        await ctx.send(f"{self.bot.latency * 1000 :.0f} ms")

    @commands.command(name='godzina')
    async def time(self, ctx: commands.Context):
        await ctx.send("w pół do komina")

    @commands.command(name='report')
    async def report(self, _, *msg: str):
        """
        Send a feedback message to the bot's owner
        """
        await (await self.bot.fetch_user(self.bot.owner_id)).send(' '.join(msg))

    @commands.command(name='dm')
    @commands.is_owner()
    async def report(self, _, user_id, *msg: str):
        """
        Send a feedback message to the bot's owner
        """
        await (await self.bot.fetch_user(int(user_id))).send(' '.join(msg))

    @commands.command(name='kill', hidden=True)
    @commands.is_owner()
    async def kill(self, ctx: commands.Context):
        await ctx.send("bye bye")
        await self.bot.close()

    @commands.command(name='echo', hidden=True)
    @commands.is_owner()
    async def echo(self, ctx: commands.Context, *msg: str):
        asyncio.create_task(ctx.message.delete())
        await ctx.send(" ".join(msg))

    @commands.command(name='warn', hidden=True)
    @commands.is_owner()
    async def warn(self, ctx: commands.Context, user: str, *msg: str):
        if user == 'all':
            with open("warns.log", "r", encoding='utf-8') as log_file:
                await ctx.send(log_file.read())
                return

        date = datetime.datetime.now().strftime("[%y/%m/%d %H:%M:%S]")
        reason = ' '.join(msg)
        await ctx.send(f"{user} has been warned!\nReason: {reason}")
        user = ctx.message.guild.get_member(int(user[2:-1])).nick
        with open("warns.log", "a", encoding='utf-8') as log_file:
            log_file.write(f"{date} {user}: {reason}\n")


