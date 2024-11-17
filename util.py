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
        }
    }
    return mapping[usage][lang]


class Word:

    def __init__(self, text: str, lang: str) -> None:
        assert (lang in ['en', 'zh'])
        self.text: str = text
        self.lang: str = lang

    def translate(self, lang_to: str, translator: Translator) -> "Meaning":
        res = translator.translate(self.text,
                                   get_lang('translate', self.lang),
                                   lang_to)

        words = map(lambda x: Word(x, lang_to), res)

        return Meaning(words)

    @staticmethod
    def from_region_dict(region: dict) -> 'Word':
        text: str = region['text']
        lang: str = get_lang('ocr_res', region['lang'])

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