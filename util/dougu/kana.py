from difflib import SequenceMatcher

ROMAJI = []
with open("util/dougu/romaji.txt", "r", encoding="utf-8") as file:
    for line in file:
        ROMAJI.append(line.strip().split('/'))


def is_hiragana(char: str) -> bool:
    return 0x3040 <= ord(char[0]) < 0x30A0


def is_katakana(char: str) -> bool:
    return 0x30A0 <= ord(char[0]) < 0x3100


def is_kana(char: str) -> bool:
    return 0x3040 <= ord(char[0]) < 0x30E0


def is_kanji(char: str) -> bool:
    return (
            0x4E00 <= ord(char[0]) < 0xA000 or
            0x3400 <= ord(char[0]) < 0x4DC0 or
            0xF900 <= ord(char[0]) < 0xFB00 or
            0x20000 <= ord(char[0]) < 0x323B0
    )


def kata2hira(katakana: str) -> str:
    if is_katakana(katakana):
        return "".join(chr(ord(i) - 0x60) for i in katakana)
    return katakana


def hira2kata(hiragana: str) -> str:
    if is_hiragana(hiragana):
        return "".join(chr(ord(i) + 0x60) for i in hiragana)
    return hiragana


def kana2romaji(kana: str) -> str:
    for rule in ROMAJI:
        kana = kana.replace(*rule)
    return kana


def combine_furigana(text: str, reading: str, furigana_format='{0}({1})') -> str:
    matcher = SequenceMatcher(None, text, reading)
    return_string = ''
    for opcode, text_from, text_to, reading_from, reading_to in matcher.get_opcodes():
        if opcode == 'equal':
            return_string += text[text_from:text_to]
        else:
            return_string += furigana_format.format(
                text[text_from:text_to], kata2hira(reading[reading_from:reading_to]))
    return return_string
