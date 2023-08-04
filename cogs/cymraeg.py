from random import choice

import aiohttp
from discord import Embed, Colour, File
from discord.ext import commands
from data.kanji_data import Kanji
from util.infix_parser import str_to_set


class Cymraeg (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cy')
    async def show_info(self, ctx: commands.Context, *args: str):
        """
        checks the grammar of a Welsh sentence
        """
        sentence = ' '.join(args)
        response = await send_request(sentence)
        total = ""
        last = 0
        for result in response['result']:
            start, end = result['start'], result['start'] + result['length']
            total += sentence[last:start] + ('\n' if last != start else '')
            total += f"{sentence[start:end]} > {result['suggestions'][0]} ({result['message']})\n"
            last = end
        total += sentence[last:]

        await ctx.send(f"```{total}```")


API_URL = \
    "https://api.techiaith.org/cysill/v1/?api_key=79bbc51e-5edc-4eb6-843b-8a7131b64f62&lang=en&text={}&max_errors=0"


async def send_request(sentence: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL.format(sentence)) as response:
            return await response.json()
