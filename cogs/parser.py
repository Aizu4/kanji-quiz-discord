from discord.ext import commands

from util.dougu.kana import *
from util.dougu.tokenizer import tokenize
from util.paginate import paginate


class Parser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("parse")
    async def parse(self, ctx: commands.Context, arg: str):
        """
        bububbubububu
        """
        for page in paginate('\n'.join(map(str, tokenize(arg)))):
            await ctx.send(f"```{page}```")

    @commands.command("furigana", aliases=["furi"])
    async def furigana(self, ctx: commands.Context, *args: str):
        text = " ".join(args)
        output = ""
        for tag in tokenize(text):
            furigana = combine_furigana(tag.surface, tag.reading)
            output += furigana
        for page in paginate(output, split_on="。"):
            await ctx.send(f"```{page}```")

    @commands.command("romaji")
    async def romaji(self, ctx: commands.Context, arg: str):
        await ctx.send(" ".join(kana2romaji(token.reading) for token in tokenize(arg)))

