from discord import Message

from .quiz_instance import QuizInstance
from discord.ext import commands

quiz_instances = dict[int, QuizInstance]()


async def start(ctx: commands.Context, *params):
    if ctx.channel.id in quiz_instances:
        return await ctx.send("There's a quiz already running on this channel")

    try:
        quiz_instance = QuizInstance(ctx, *params)
    except ValueError:
        return await ctx.send("No deck specified")

    quiz_instances[ctx.channel.id] = quiz_instance
    await quiz_instance.run()
    del quiz_instances[ctx.channel.id]


async def stop(ctx: commands.Context):
    if ctx.channel.id not in quiz_instances:
        return await ctx.send("No quiz")

    quiz_instances[ctx.channel.id].kill()
    del quiz_instances[ctx.channel.id]
