import asyncio

import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

from cogs.debug import Debug
from cogs.quiz import Quiz
from cogs.info import Info

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="k?", owner_id=int(os.getenv('OWNER')), intents=intents)


@bot.event
async def on_ready():
    print('ready')


async def main():
    await bot.add_cog(Debug(bot))
    await bot.add_cog(Info(bot))
    await bot.add_cog(Quiz(bot))
    await bot.start(os.getenv('TOKEN'))


if __name__ == '__main__':
    asyncio.run(main())
