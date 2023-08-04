from __future__ import annotations

from dataclasses import dataclass
from pprint import pprint

from data.raw_data import raw_data

whole_data: dict[str, Kanji]
kanji_sets: dict[str, set[str]]


@dataclass
class Kanji:
    literal: str
    grade: int | None
    jlpt: int | None
    strokes: int | None
    freq: int | None
    on_yomi: list[str]
    kun_yomi: list[str]
    quiz_yomi: set[str]
    meanings: list[str]

    def on_yomi_str(self) -> str:
        if self.on_yomi:
            return '、'.join(self.on_yomi)
        return '-'

    def kun_yomi_str(self) -> str:
        if self.kun_yomi:
            return '、'.join(self.kun_yomi)
        return '-'

    def meanings_str(self) -> str:
        if self.meanings:
            return '; '.join(self.meanings)
        return '-'

    def type_str(self) -> str:
        if self.grade is None:
            return ''
        elif self.grade < 6:
            return 'Kyouiku kanji'
        elif self.grade == 7:
            return 'Jouyou kanji'
        else:
            return 'Jinmeiyou kanji'

    @classmethod
    def from_local(cls, literal: str) -> Kanji:
        return whole_data.get(literal)

    @staticmethod
    def get_set(set_name: str) -> set[str]:
        try:
            return kanji_sets[set_name]
        except KeyError:
            return set()


whole_data = dict((k, Kanji(*v)) for k, v in raw_data.items())

kanji_sets: dict[str, set[str]] = {
    'all': set(k for k in whole_data.keys()),

    'n5': set(k for k, d in whole_data.items() if d.jlpt == 5),
    'n4': set(k for k, d in whole_data.items() if d.jlpt == 4),
    'n3': set(k for k, d in whole_data.items() if d.jlpt == 3),
    'n2': set(k for k, d in whole_data.items() if d.jlpt == 2),
    'n1': set(k for k, d in whole_data.items() if d.jlpt == 1),
    'n0': set(k for k, d in whole_data.items() if d.jlpt == 0),

    'g1': set(k for k, d in whole_data.items() if d.grade == 1),
    'g2': set(k for k, d in whole_data.items() if d.grade == 2),
    'g3': set(k for k, d in whole_data.items() if d.grade == 3),
    'g4': set(k for k, d in whole_data.items() if d.grade == 4),
    'g5': set(k for k, d in whole_data.items() if d.grade == 5),
    'g6': set(k for k, d in whole_data.items() if d.grade == 6),
    'g7': set(k for k, d in whole_data.items() if d.grade == 7),
    'g8': set(k for k, d in whole_data.items() if d.grade == 8),
    'gx': set(k for k, d in whole_data.items() if d.grade is None),

    'kyouiku': set(k for k, d in whole_data.items() if d.grade in [1, 2, 3, 4, 5, 6]),
    'jouyou': set(k for k, d in whole_data.items() if d.grade in [1, 2, 3, 4, 5, 6, 7]),
    'jinmeiyou': set(k for k, d in whole_data.items() if d.grade is not None),

    'f500':  set(k for k, d in whole_data.items() if (d.freq is not None and d.freq <= 500)),
    'f1000':  set(k for k, d in whole_data.items() if (d.freq is not None and d.freq <= 1000)),
    'f1500':  set(k for k, d in whole_data.items() if (d.freq is not None and d.freq <= 1500)),
    'f2000':  set(k for k, d in whole_data.items() if (d.freq is not None and d.freq <= 2000)),
    'f2500':  set(k for k, d in whole_data.items() if (d.freq is not None and d.freq <= 2500)),
    'fnone':  set(k for k, d in whole_data.items() if d.freq is None),
}

for f in range(500, 2501, 500):
    kanji_sets[f"f{f}"] = set(k for k, d in whole_data.items() if (d.freq is not None and d.freq <= 500))


if __name__ == '__main__':
    with open("kanken.txt", 'r', encoding='utf-8') as kanken_file:
        kanken = set(k for k in kanken_file.read())

    with open("out.json", "w", encoding="utf-8") as json_file:
        to_write = ""
        to_write += "[\n"
        for k in whole_data.values():
            if k.literal not in kanken:
                continue
            to_write += "\t{"
            for attr in ['literal', 'grade', 'jlpt', 'freq', 'strokes', 'on_yomi', 'kun_yomi', 'meanings']:
                if value := k.__getattribute__(attr):
                    to_write += f"{attr!r}:{value!r},"
            to_write += "},\n"
        to_write += "]"
        to_write = to_write.replace(",}", "}"). replace(",]", "]") \
            .replace(",'", ",\"").replace("{'", "{\"").replace("['", "[\"").replace(", '", ", \"").replace(":'", ":\"") \
            .replace("':", "\":").replace("',", "\",").replace("']", "\"]").replace("'}", "\"}")
        json_file.write(to_write)

