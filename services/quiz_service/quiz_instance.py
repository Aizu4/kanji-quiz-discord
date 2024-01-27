import asyncio
from collections import Counter
from typing import Generator

import jaconv
from discord import Message, Member, Embed, Color
from discord.ext import commands

from services.question_service import Question, Deck


class WrongAnswerException(Exception):
    pass


class QuizInstance:
    loop_handler: asyncio.Task

    max_score: int = 10
    max_incorrect: int = 5
    answer_time: int = 10
    additional_time: int = 1
    hardcore: bool = False

    scores: Counter[Member, int]
    players_answered: set[Member]
    mistakes: int = 0

    question: Question

    def __init__(self, ctx: commands.Context, deck: str = None, *params: str):
        if not deck:
            raise ValueError('No deck specified')

        self.bot = ctx.bot
        self.ctx = ctx
        self.scores = Counter()
        self.players_answered = set()
        self.deck = Deck.from_server(deck)
        self.init_params(params)

    def init_params(self, params: tuple[str, ...]):
        for param in params:
            if param == 'nodelay':
                self.additional_time = 0
            elif param == 'hardcore':
                self.hardcore = True
            elif param.startswith('maxfail='):
                self.max_incorrect = int(param[8:])
            elif param.startswith('anstime='):
                self.answer_time = int(param[8:])
            elif param.startswith('addtime='):
                self.additional_time = int(param[8:])
            elif param.isnumeric():
                self.max_score = int(param)

    async def run(self):
        await self.send_start()

        try:
            self.loop_handler = asyncio.create_task(self.loop())
            await self.loop_handler
        except asyncio.CancelledError:
            await self.send_abort()
        except Exception as e:
            await self.ctx.send(f'Error: {e}')
        finally:
            await self.send_finish()

    async def loop(self):
        while not self.check_finish():
            try:
                self.question = next(self.deck.questions)
                await self.send_question()
                await self.bot.wait_for('message', check=self.accept_answer, timeout=self.answer_time)
                await self.bot.wait_for('message', check=self.accept_additional_answer, timeout=self.additional_time)
            except asyncio.TimeoutError:
                if self.players_answered:
                    await self.send_correct_answer()
                else:
                    self.mistakes += 1
                    await self.send_no_answer()
            except WrongAnswerException:
                self.mistakes += 1
                await self.send_incorrect_answer()
            finally:
                for player in self.players_answered:
                    self.scores[player] += 1
                self.players_answered.clear()

    def kill(self):
        self.loop_handler.cancel()

    def accept_answer(self, msg: Message) -> bool:
        if msg.channel.id != self.ctx.channel.id:
            return False
        if msg.author.id == self.bot.user.id:
            return False
        if not self.check_answer(msg):
            return False

        self.players_answered.add(msg.author)
        return True

    def accept_additional_answer(self, msg: Message) -> bool:
        self.accept_answer(msg)
        return False

    def check_answer(self, answer: Message):
        content = answer.content.strip()
        if content == 's':
            raise asyncio.TimeoutError
        if content in self.question.answers:
            return True
        elif jaconv.alphabet2kana(content) in self.question.answers:
            return True
        elif jaconv.alphabet2kata(content) in self.question.answers:
            return True

        if self.hardcore:
            raise WrongAnswerException

        return False

    def check_finish(self) -> bool:
        if self.scores and self.scores.most_common(1)[0][1] >= self.max_score:
            return True
        return self.mistakes > self.max_incorrect

    # === EMBEDS === #

    async def send_start(self):
        await self.ctx.send(
            embed=Embed(
                title='Quiz started',
                description=f'Number of questions: {self.deck.size}',
                color=Color.dark_blue()
            )
        )

    async def send_question(self):
        await self.ctx.send(
            embed=Embed(
                title="Type the answer! (s to skip)",
                description=self.question.instruction,
                color=Color.blue()
            )
        )

    async def send_finish(self):
        await self.ctx.send(
            embed=Embed(
                title='Quiz finished',
                description='\n'.join(f'{player.display_name}: {score}' for player, score in self.scores.most_common()),
                color=Color.dark_green()
            )
        )

    async def send_abort(self):
        await self.ctx.send(
            embed=Embed(
                title='Quiz cancelled',
                color=Color.dark_red()
            )
        )

    async def send_correct_answer(self):
        await self.ctx.send(
            embed=Embed(
                title='Correct!',
                description=self.question.formatted_description(),
                color=Color.green(),
            )
        )

    async def send_incorrect_answer(self):
        await self.ctx.send(
            embed=Embed(
                title='Incorrect',
                description=self.question.formatted_description(),
                color=Color.red(),
            )
        )

    async def send_no_answer(self):
        await self.ctx.send(
            embed=Embed(
                title='No answer',
                description=self.question.formatted_description(),
                color=Color.red(),
            )
        )

    async def send_invalid_deck(self):
        await self.ctx.send(
            embed=Embed(
                title='Invalid deck',
                description='There is no deck with that name',
                color=Color.red(),
            )
        )
