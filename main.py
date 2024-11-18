import sys
import time

from translate import Translator
from ocr import Screen
from util import get_lang, print_time


def main():
    side = sys.argv[1]

    translator = Translator()
    screen = Screen(side)

    print(f'listening on {side} side')
    time.sleep(4)
    while True:
        try:
            word, meanings = screen.ocr()
        except Exception as e:
            print(e)
            continue

        translate = word.translate(get_lang('translate', screen.config.lang_to), translator)
        for meaning in meanings:
            if translate == meaning:
                meaning.click()

        time.sleep(0.5)


def test():
    side = 'left'

    translator = Translator()
    screen = Screen(side)

    print(f'listening on {side} side')
    time.sleep(4)
    while True:
        loop(screen, translator)


@print_time
def loop(screen: Screen, translator: Translator) -> None:
    try:
        word, meanings = print_time(screen.ocr)()
        print(f'Word: {word}')
        print(f'Meanings: {meanings}')
    except Exception as e:
        print(e)
        return

    translated = print_time(word.translate)(get_lang('translate', screen.config.lang_to), translator)
    print(f'Translated: {translated}')
    for meaning in meanings:
        if translated == meaning:
            meaning.click()
            print(f'clicked {meaning}')

    time.sleep(1)


if __name__ == "__main__":
    # main()
    test()
    pass
