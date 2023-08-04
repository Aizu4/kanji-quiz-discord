import asyncio

import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

from cogs.debug import Debug
from cogs.parser import Parser
from cogs.quiz import Quiz
from cogs.info import Info
from cogs.cymraeg import Cymraeg

load_dotenv()

bot = commands.Bot(command_prefix="yo!", owner_id=int(os.getenv('OWNER')), intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('ready')


async def main():
    await bot.add_cog(Debug(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Quiz(bot))
    await bot.add_cog(Parser(bot))
    await bot.add_cog(Cymraeg(bot))
    await bot.start(os.getenv('TOKEN'))


if __name__ == '__main__':
    asyncio.run(main())
