import sys

from translate import Translator
from ocr import Screen, Rect, Point
from util import get_lang

class Config:
    def __init__(self, screen: 'Screen'):
        self.word_img_filename = 'word_img.png'
        self.meanings_img_filename = 'meanings_img.png'
        self.lang_from = 'en'
        self.lang_to = 'zh'
        self.left_word_rect = Rect(Point(700/3840, 670/2160, screen),
                                   Point(1300/3840, 740/2160, screen))
        self.right_word_rect = Rect(Point(2500/3840, 670/2160, screen),
                                    Point(3100/3840, 740/2160, screen))
        self.left_meanings_rect = Rect(Point(330/3840, 960/2160, screen),
                                       Point(1680/3840, 2020/2160, screen))
        self.right_meanings_rect = Rect(Point(2100/3840, 960/2160, screen),
                                        Point(3480/3840, 2020/2160, screen))

def main():
    side = sys.argv[1]

    translator = Translator()
    screen = Screen(side)

    print(f'listening on {side} side')
    while True:
        ocr_res = screen.ocr()
        if ocr_res is not None:
            word, meanings = ocr_res
        else:
            continue

        translate = word.translate(get_lang('translate', screen.config.lang_to), translator)
        for meaning in meanings:
            if translate == meaning:
                meaning.click()

if __name__ == "__main__":
    main()