from dataclasses import dataclass

from janome.tokenizer import Tokenizer, Token

from .kana import *

PARTS_OF_SPEECH = {
    '名詞': 'NOUN',
    '代名詞': 'PRONOUN',
    '動詞': 'VERB',
    'サ変接続': 'SURU-VERB',
    '助動詞': 'AUX-VERB',
    '副詞': 'ADVERB',
    '副詞可能': 'ADVERB-LIKE',
    '形容詞': 'I-ADJECTIVE',
    '形容動詞語幹': 'NA-ADJECTIVE',
    '接続詞': 'CONJUNCTION',

    '助詞': 'PARTICLE',
    '係助詞': 'BINDING',
    '接続助詞': 'CONJUNCTION',
    '格助詞': 'CASE',
    '並立助詞': 'PARALLEL',
    '連体化': 'ADNOMIAL',

    '一般': 'GENERAL',
    '自立': 'INDEPENDENT',
    '非自立': 'DEPENDENT',
    '連語': 'COMPOUND',

    '記号': 'SYMBOL',
    '読点': 'COMMA',
    '句点': 'PERIOD',
}

INFLECTION_TYPES = {
    '一段': 'ICHIDAN',
    '五段・ナ行': 'GODAN-NU',
    'サ変・スル': 'IRR-SURU',
    '*': ''
}

INFLECTION_FORMS = {
    '基本形': 'BASE',
    '連用形': 'MASU-STEM',
    '連用タ接続': 'TE-STEM',
    '*': ''
}


def _translate(tag: str) -> str:
    return PARTS_OF_SPEECH.get(tag) or INFLECTION_TYPES.get(tag) or INFLECTION_FORMS.get(tag) or tag


@dataclass
class TokenWrapper:
    surface: str
    part_of_speech: list[str]
    infl_type: str
    infl_form: str
    base_form: str
    reading: str
    phonetic: str

    def __init__(self, token: Token, translate=True):
        self.surface = token.surface
        self.reading = token.reading if is_katakana(token.surface) else \
            kata2hira(token.reading) if token.reading != '*' else token.surface
        self.phonetic = token.phonetic if token.phonetic != '*' else token.surface
        self.base_form = token.base_form

        if not translate:
            self.part_of_speech = [p for p in token.part_of_speech.split(',') if p != '*']
            self.infl_type = token.infl_type
            self.infl_form = token.infl_form
        else:
            self.part_of_speech = [_translate(p) for p in token.part_of_speech.split(',') if p != '*']
            self.infl_type = _translate(token.infl_type)
            self.infl_form = _translate(token.infl_form)

    def __str__(self):
        return '\t'.join(map(str, self.__dict__.values()))


def tokenize(text: str, translate=True, tokenizer=Tokenizer()) -> list[TokenWrapper]:
    return [TokenWrapper(token, translate) for token in tokenizer.tokenize(text)]
