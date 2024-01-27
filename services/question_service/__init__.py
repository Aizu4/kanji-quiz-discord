from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Generator

import requests


@dataclass
class Question:
    instruction: str
    answers: list[str]
    content: str

    @classmethod
    def from_json(cls, data: dict) -> Question:
        return cls(
            instruction=data['front'],
            answers=data['back'].split(','),
            content=data['notes'] + '\n' + data['example_front'] + '\n' + data['example_back']
        )

    def formatted_description(self) -> str:
        return '\n'.join(f'{i}. {answer}' for i, answer in enumerate(self.answers, start=1)) + '\n' + self.content


@dataclass
class Deck:
    name: str
    size: int
    questions: Generator

    @classmethod
    def from_server(cls, slug: str) -> Deck:
        response = requests.get(os.getenv('BACKEND_URL') + 'decks/s/' + slug)
        response.raise_for_status()
        data = response.json()
        questions = [Question.from_json(q) for q in data['card_set']]
        random.shuffle(questions)

        def generator(): yield from questions

        deck = cls(
            name=data['name'],
            size=len(data['card_set']),
            questions=generator()
        )
        return deck
