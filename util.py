import time
from collections.abc import Iterable

from translate import Translator


def get_lang(usage: str, lang: str) -> str:
    mapping = {
        'ocr': {
            'en': 'en',
            'zh': 'zh-CHS',
        },
        'ocr_res': {
            'en': 'en',
            'zh': 'zh',
        },
        'translate': {
            'en': 'EN',
            'zh': 'zh-CHS',
        },
        'translate_res': {
            'EN': 'en',
            'zh-CHS': 'zh',
        },
    }
    return mapping[usage][lang]


class Word:

    def __init__(self, text: str, lang: str) -> None:
        assert (lang in ['en', 'zh'])
        self.text: str = text
        self.lang: str = lang

    def translate(self, lang_to: str, translator: Translator) -> 'Meaning':
        res = translator.translate(self.text,
                                   get_lang('translate', self.lang),
                                   lang_to)

        words = map(lambda x: Word(x, get_lang('translate_res', lang_to)), res)

        return Meaning(words)

    @staticmethod
    def from_region_dict(region: dict) -> 'Word':
        line: dict = region['lines'][0]

        text: str = line['text']
        # lang: str = get_lang('ocr_res', line['lang']) # ocr result unreliable
        lang: str = 'en'

        return Word(text, lang)

    def __repr__(self):
        return f"Word {self.text} in {self.lang}"

    def __eq__(self, value: "Word") -> bool:
        return self.text == value.text


class Meaning:

    def __init__(self, words: Iterable[Word]) -> None:
        self.words: list[Word] = list(words)

    def __repr__(self):
        return f"Meaning {self.words}"

    def __eq__(self, value: "Meaning") -> bool:
        for word in self.words:
            if word in value.words:
                return True
        return False


def print_time(f):
    def new_f(*args, **kwargs):
        start = time.time()
        res = f(*args, **kwargs)
        end = time.time()
        print(f'{f.__name__} time: {end - start}')
        return res

    return new_f
