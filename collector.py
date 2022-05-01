from bs4 import BeautifulSoup
from data.kanji_data import whole_data
from PIL import Image, ImageDraw, ImageFont

import jaconv

SIZE = 128
CENTER = (SIZE / 2, SIZE * 0.9 / 2)
FONT = ImageFont.truetype('./NotoSansJP-Regular.otf', size=int(SIZE*0.95))


def render_kanji(kanji: str):
    image = Image.new('L', (SIZE, SIZE), 'white')
    canvas = ImageDraw.Draw(image)
    canvas.text(
        CENTER, kanji,
        anchor='mm',
        align='center',
        font=FONT,
    )
    image.save(f"kanji_renders/{kanji}.png")


def render_all_kanji():
    for k in whole_data:
        render_kanji(k)


def xml2kanji():
    with open('kanjidic2.xml', 'r', encoding='utf-8') as kanjidic:
        soup = BeautifulSoup(kanjidic.read())

    jlpt_data = dict()

    with open('Kanji_20220419_011651.csv', 'r', encoding='utf-8') as kanjicsv:
        for line in kanjicsv.readlines():
            jlpt_data[line[0]] = int(line[-2])

    characters = soup.find_all('character')

    raw_data: dict[str, tuple] = {}

    for c in characters:
        literal = c.find('literal').get_text()

        grade = int(x.get_text()) if (x := c.find('grade')) is not None else -1
        jlpt = jlpt_data[literal] if literal in jlpt_data else 0
        strokes = int(x.get_text()) if (x := c.find('stroke_count')) is not None else None
        freq = int(x.get_text()) if (x := c.find('freq')) is not None else None

        # grade correction
        if grade == 8:
            grade = 7
        elif grade > 8:
            grade = 8
        elif grade == -1:
            grade = None

        on_yomi = list(dict.fromkeys([r.get_text().replace('-', '') for r in c.find_all('reading', r_type='ja_on')]))
        kun_yomi = list(dict.fromkeys([r.get_text().replace('-', '') for r in c.find_all('reading', r_type='ja_kun')]))
        meanings = [r.get_text() for r in c.find_all('meaning')]

        quiz_yomi = set(jaconv.kata2hira(yomi.replace('.', '').replace('-', '')) for yomi in on_yomi + kun_yomi)

        if not quiz_yomi:
            continue

        if not meanings:
            continue

        raw_data[literal] = (literal, grade, jlpt, strokes, freq, on_yomi, kun_yomi, quiz_yomi, meanings)

    with open('data/raw_data.py', 'w', encoding='utf-8') as output:
        output.write("raw_data = {\n")
        for k, d in raw_data.items():
            output.write(f"    '{k}': {repr(d)},\n")
        output.write("}")


if __name__ == '__main__':
    # xml2kanji()
    render_all_kanji()
