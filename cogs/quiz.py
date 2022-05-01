from __future__ import annotations

import asyncio

from discord import Colour, Message, Embed, File
from discord.ext import commands, tasks

from enum import Enum
from collections import Counter
from typing import Generator

from random import shuffle
from jaconv import alphabet2kana

from data import kanji_data
from data.kanji_data import Kanji

# constraints
from util.infix_parser import str_to_set

_MIN_POINTS = 1
_MAX_POINTS = 1000
_MIN_TIME = 1
_MAX_TIME = 60
_MIN_ADD_TIME = 0
_MAX_ADD_TIME = 10

_MAX_WRONG_STREAK = 10


class _EmbedType(Enum):
    START = 0
    ASK = 1
    CORRECT = 2
    WRONG = 3
    SCORES = 4
    FINISHED = 10
    STOPPED = 11


class _GameState(Enum):
    START = 0
    CORRECT = 1
    WRONG = 2
    FINISHED = 10
    STOPPED = 11


class QuizInstance:
    ctx: commands.Context

    # static
    current_games: dict[int, QuizInstance] = dict()

    max_points: int
    answer_time: int
    additional_time: int

    set_size: int

    _current_kanji: Kanji
    _kanji_stream: Generator[Kanji]

    _scores: Counter[int, int]
    _people_answered: set[int]
    _wrong_streak: int

    _game_state: _GameState
    _lock: bool = False

    def __init__(self, ctx: commands.Context, bot, *params: str):
        self.ctx = ctx
        self.bot = bot

        question_set, self.max_points, self.answer_time, self.additional_time = self._parse_select(*params)

        self.set_size = len(question_set)

        if not question_set:
            raise KeyError('The answer stream is empty')

        if not (_MIN_POINTS <= self.max_points <= _MAX_POINTS):
            raise KeyError()

        if not (_MIN_TIME <= self.answer_time <= _MAX_TIME):
            raise KeyError()

        if not (_MIN_ADD_TIME <= self.additional_time <= _MAX_ADD_TIME):
            raise KeyError()

        self._wrong_streak = 0
        self._game_state = _GameState.START
        self._scores = Counter()
        self._kanji_stream = QuizInstance._random_stream(question_set)

    @tasks.loop()
    async def ask(self):
        self.lock()
        match self._game_state:
            case _GameState.START:
                await self._send_embed(_EmbedType.START)

            case _GameState.CORRECT | _GameState.FINISHED:
                self._wrong_streak = 0
                await self._send_embed(_EmbedType.CORRECT)
                await self._send_embed(_EmbedType.SCORES)

            case _GameState.WRONG:
                self._wrong_streak += 1
                await self._send_embed(_EmbedType.WRONG)
                await self._send_embed(_EmbedType.SCORES)

        self._current_kanji = next(self._kanji_stream)
        self.unlock()

        if self._game_state == _GameState.FINISHED:
            self.ask.cancel()
            return

        if self._wrong_streak >= _MAX_WRONG_STREAK:
            self.stop()
            return

        await asyncio.sleep(1)

        self._game_state = _GameState.WRONG

        self._people_answered = set()

        await self._send_embed(_EmbedType.ASK)

    @ask.after_loop
    async def after_ask(self):
        if self._game_state == _GameState.FINISHED:
            await self._send_embed(_EmbedType.FINISHED)
            return

        if self._game_state == _GameState.STOPPED:
            await self._send_embed(_EmbedType.STOPPED)
            return

        if (best_players := self._scores.most_common()) and best_players[0][1] >= self.max_points:
            self.finish()

    async def run(self):
        if self.ctx.channel.id in self.current_games:
            await self.ctx.send(embed=Embed(title="A quiz is already running on this channel!"))
            return
        self.current_games[self.ctx.channel.id] = self
        self.ask.change_interval(seconds=self.answer_time + self.additional_time + 1)
        self.ask.start()

    def stop(self):
        self._game_state = _GameState.STOPPED
        self.ask.cancel()
        del self.current_games[self.ctx.channel.id]

    def finish(self):
        self._game_state = _GameState.FINISHED
        self.ask.cancel()
        del self.current_games[self.ctx.channel.id]

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False

    def is_locked(self) -> bool:
        return self._lock

    async def _send_embed(self, embed_type: _EmbedType):
        match embed_type:
            case _EmbedType.START:
                embed = Embed(title=f"The quiz starts soon! ({self.set_size} kanji in total)", colour=Colour.blue())
                await self.ctx.send(embed=embed)

            case _EmbedType.ASK:
                kanji = self._current_kanji
                file = File(f"kanji_renders/{kanji.literal}.png", filename="image.png")
                embed = Embed(colour=Colour.darker_grey()) \
                    .set_image(url="attachment://image.png")
                await self.ctx.send(file=file, embed=embed)

            case _EmbedType.CORRECT:
                kanji = self._current_kanji
                embed = Embed(title='The answer is correct', description=kanji.literal, colour=Colour.green()) \
                    .add_field(name="On'yomi", value=kanji.on_yomi_str(), inline=False) \
                    .add_field(name="Kun'yomi", value=kanji.kun_yomi_str(), inline=False) \
                    .add_field(name="Meanings", value=kanji.meanings_str(), inline=False)
                await self.ctx.send(embed=embed)

            case _EmbedType.WRONG:
                kanji = self._current_kanji
                embed = Embed(title='The answer is wrong', description=kanji.literal, colour=Colour.red()) \
                    .add_field(name="On'yomi", value=kanji.on_yomi_str(), inline=False) \
                    .add_field(name="Kun'yomi", value=kanji.kun_yomi_str(), inline=False) \
                    .add_field(name="Meanings", value=kanji.meanings_str(), inline=False)
                await self.ctx.send(embed=embed)

            case _EmbedType.SCORES:
                user = self.bot.fetch_user
                embed = Embed(
                    title=f"Scores: (playing to {self.max_points})",
                    colour=Colour.blue(),
                    description="\n".join(
                        [f"{(await user(uid)).display_name} : {score}" for uid, score in self._scores.most_common()])
                )
                await self.ctx.send(embed=embed)

            case _EmbedType.FINISHED:
                embed = Embed(title="You have finished the quiz!", colour=Colour.green())
                await self.ctx.send(embed=embed)

            case _EmbedType.STOPPED:
                embed = Embed(title="The quiz has been stopped!", colour=Colour.red())
                await self.ctx.send(embed=embed)

    async def process_answer(self, msg: Message):
        if self.is_locked():
            return

        author_id = msg.author.id
        if author_id in self._people_answered:
            return

        if msg.content in ['s', '.', '。', 'ｓ']:
            self.ask.restart()
            return

        answer = alphabet2kana(msg.content.strip())
        if answer in self._current_kanji.quiz_yomi:
            if author_id not in self._people_answered:
                self._people_answered.add(author_id)
                self._scores[author_id] += 1

            if len(self._people_answered) == 1:
                self._game_state = _GameState.CORRECT
                self.ask.cancel()
                await asyncio.sleep(self.additional_time)
                self.ask.start()

    @staticmethod
    def _random_stream(items: list[any]) -> any:
        while True:
            shuffle(items)
            for i in items:
                yield i

    @staticmethod
    def _parse_select(set_param: str, max_points: str = '10', answer_time: str = '10', additional_time: str = '2') \
            -> tuple[list[Kanji], int, int, int]:
        final_set = str_to_set(set_param, Kanji.get_set)
        kanji_list = list(Kanji.from_local(k) for k in final_set)
        return kanji_list, int(max_points), int(answer_time), int(additional_time)


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start')
    async def start_quiz(self, ctx: commands.Context, *arg: str):
        """
        Starts a new game of guessing the readings of kanji
        """
        if not arg:
            embed = Embed(
                title="Available kanji decks:",
                description=", ".join(kanji_data.kanji_sets.keys())
            )
            await ctx.send(embed=embed)
            return

        try:
            await QuizInstance(ctx, self.bot, *arg).run()
        except KeyError:
            await ctx.send(embed=Embed(title="Invalid command arguments"))
        except IndexError:
            await ctx.send(embed=Embed(title="Invalid kanji set expression"))

    @commands.command(name='stop')
    async def stop_quiz(self, ctx: commands.Context):
        """
        Stops an ongoing game in the channel
        """
        if (channel_id := ctx.channel.id) in QuizInstance.current_games:
            QuizInstance.current_games[channel_id].stop()
        else:
            await ctx.send(embed=Embed(title="There is not any running game on this channel!"))

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        if msg.author.id == self.bot.user.id:  # Check if the bot itself isn't the author
            return

        if msg.content.startswith(self.bot.command_prefix):  # Ignore all commands
            return

        if msg.channel.id not in QuizInstance.current_games:  # Ignore all messages that aren't on an active channel
            return

        game = QuizInstance.current_games[msg.channel.id]
        await game.process_answer(msg)
