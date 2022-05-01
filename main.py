from discord.ext import commands

import os
from dotenv import load_dotenv

# Import cogs
from cogs.debug import Debug
from cogs.quiz import Quiz
from cogs.info import Info

load_dotenv()

bot = commands.Bot(command_prefix="k?", owner_id=int(os.getenv('OWNER')))

bot.add_cog(Quiz(bot))
bot.add_cog(Debug(bot))
bot.add_cog(Info(bot))


@bot.event
async def on_ready():
    print('ready')


if __name__ == '__main__':
    token = os.getenv('TOKEN')
    bot.run(token)
