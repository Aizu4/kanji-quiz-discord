from discord import Embed, Colour, File
from discord.ext import commands
from data.kanji_data import Kanji


class Info (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info')
    async def show_info(self, ctx: commands.Context, arg: str):
        """
        Displays info for given kanji character
        """
        try:
            kanji = Kanji.from_local(arg)
        except KeyError:
            await ctx.send('Invalid kanji')
            return

        file = File(f"kanji_renders/{kanji.literal}.png", filename="image.png")

        embed = Embed(title=kanji.literal, description=kanji.type_str(), colour=Colour.blue()) \
            .set_image(url="attachment://image.png") \
            .add_field(name="On'yomi", value=kanji.on_yomi_str(), inline=False) \
            .add_field(name="Kun'yomi", value=kanji.kun_yomi_str(), inline=False) \
            .add_field(name="Meanings", value=kanji.meanings_str(), inline=False)

        await ctx.send(file=file, embed=embed)

