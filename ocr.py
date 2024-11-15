import base64
from itertools import cycle
from collections.abc import Iterable

import requests
import pyautogui

from AuthV3Util import addAuthParams
from translate import Translator

class OCRAPI:

    def __init__(self) -> None:
        self.query_url = "https://openapi.youdao.com/ocrapi"
        self.appkey = "157438dc01f55c58"
        self.key = "fz1VVcsGrhoWtiqqehASiJz1SvSxQlTp"
        self.detect_type = '10012'
        self.image_type = '1'
        self.doc_type = 'json'
  
    def ocr(self, img_filename: str, lang: str) -> list[dict] | None:

        with open(img_filename, 'rb') as img_file:
            # < 8mb
            img = str(base64.b64encode(img_file.read()), 'utf-8')
            
        data = {'img': img,
                'langType': lang,
                'detectType': self.detect_type,
                'imageType': self.image_type,
                'docType': self.doc_type,
            }

        addAuthParams(self.appkey, self.key, data)

        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        res = requests.post(self.query_url, data, header).json()
        
        if res['errorCode'] != '0':
            raise Exception('error calling ocr api')
        
        regions = res['Result']['regions']
        
        if len(regions) == 0:
            return None
        
        return regions

class Config:
    def __init__(self):
        self.word_img_filename = 'word_img.png'
        self.meanings_img_filename = 'meanings_img.png'
        self.left_word_rect = Rect(Point(700/3840, 670/2160, self),
                                   Point(1300/3840, 740/2160, self))
        self.right_word_rect = Rect(Point(2500/3840, 670/2160, self),
                                    Point(3100/3840, 740/2160, self))
        self.left_meanings_rect = Rect(Point(330/3840, 960/2160, self),
                                       Point(1680/3840, 2020/2160, self))
        self.right_meanings_rect = Rect(Point(2100/3840, 960/2160, self),
                                        Point(3480/3840, 2020/2160, self))

class Screen:
    
    def __init__(self, ocrapi: OCRAPI, side: str, config: Config) -> None:
        self.width, self.height = pyautogui.size()
        self.ocrapi: OCRAPI = ocrapi
        self.side: str = side
        self.config = config

    def click(self, x_ratio: float, y_ratio: float) -> None:
        pyautogui.click(x_ratio*self.width, y_ratio*self.height)
    
    def ocr(self) -> tuple['Word', list['Region']] | None:
        word_rect, meanings_rect = self.get_rects()
                
        self.screenshot(self.config.word_img_filename, word_rect)
        self.screenshot(self.config.meanings_img_filename, meanings_rect)
        
        word_region = self.ocrapi.ocr(self.config.word_img_filename, 'EN')[0]
        if word_region is not None:
            word = Word.from_region_dict(word_region)
        else:
            return None
        
        meanings_region = self.ocrapi.ocr(self.config.meanings_img_filename, 'zh-CHS')
        if meanings_region is not None:
            meanings = map(Region.from_region_dict,
                        meanings_region,
                        cycle([self]))
        else:
            return None
        
        return word, meanings

    def screenshot(self, img_filename: str, rect: 'Rect') -> None:
        pyautogui.screenshot(img_filename,
                                (rect.left(),
                                rect.top(),
                                rect.width(),
                                rect.height()
                                )
                             )

    def get_rects(self):
        if self.side == 'left':
            word_rect = self.config.left_word_rect
            meanings_rect = self.config.left_meanings_rect
        elif self.side == 'right':
            word_rect = self.config.right_word_rect
            meanings_rect = self.config.right_meanings_rect
        else:
            raise Exception('side not left or right')
        
        return word_rect, meanings_rect

class Point:
    
    def __init__(self,
                 x_ratio: float,
                 y_ratio: float,
                 screen: Screen) -> None:
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.screen = screen
    
    def click(self) -> None:
        self.screen.click(self.x_ratio, self.y_ratio)
    
    def x(self) -> int:
        return round(self.x_ratio * self.screen.width)
    
    def y(self) -> int:
        return round(self.y_ratio * self.screen.height)
    
    def __add__(self, value: "Point") -> "Point":
        return Point(self.x_ratio+value.x_ratio, self.y_ratio+value.y_ratio, self.screen)
    
    def __mul__(self, value) -> "Point":
        return Point(self.x_ratio*value, self.y_ratio*value, self.screen)
    
    def __div__(self, value) -> "Point":
        return Point(self.x_ratio/value, self.y_ratio/value, self.screen)
    
    def __repr__(self):
        return f"Point({self.x_ratio}, {self.y_ratio})"

class Rect:
    
    def __init__(self, upleft: Point, downright: Point):
        self.topleft = upleft
        self.bottomright = downright
    
    def center(self) -> Point:
        return (self.topleft + self.bottomright) / 2
    
    def width(self) -> int:
        return self.right() - self.left()

    def left(self) -> int:
        return self.topleft.x()
    
    def right(self) -> int:
        return self.bottomright.x()
    
    def height(self) -> int:
        return self.bottom() - self.top()

    def top(self) -> int:
        return self.topleft.y()

    def bottom(self) -> int:
        return self.bottomright.y()

    def click(self) -> None:
        self.center().click()
    
class Word:
    
    def __init__(self, text: str, lang: str) -> None:
        self.text: str = text
        self.lang: str = lang
    
    def translate(self, target: str, translator: Translator) -> "Meaning":
        res = translator.translate(self.text,
                                   self.lang,
                                   target)
        
        words = map(lambda x: Word(x, target), res)
        
        return Meaning(words)
    
    @staticmethod
    def from_region_dict(region: dict) -> 'Word':
        text: str = region['text']
        lang: str = region['lang']
        
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

class Region(Meaning):
    def __init__(self, words: Iterable[Word], rect: Rect):
        self.words: list[Word] = list(words)
        self.rect: Rect = rect

    def click(self) -> None:
        self.rect.click()

    @staticmethod
    def from_region_dict(region: dict, screen: Screen) -> 'Region':
        text: str = region['text']
        lang: str = 'zh-CHS'
    
        rect: list[str] = region['boundingBox'].split(',')
        topleft = Point(int(rect[0]), int(rect[1]), screen)
        bottomright = Point(int(rect[4]), int(rect[5]), screen)
        rect = Rect(topleft, bottomright)
        
        words = map(lambda word: Word(word, lang), text.split(';'))
        return Region(words, rect)

    def __repr__(self):
        return f"Region {self.words}"


def test_word_and_meanings():
    translator = Translator()
    
    good = Word('good', 'EN')
    good_translate = good.translate('zh-CHS', translator)
    
    good_meaning = Meaning([Word('好', 'zh-CHS')])
    bad_meaning = Meaning([Word('坏', 'zh-CHS')])
    great_meaning = Meaning([Word('极好', 'zh-CHS')])
    meanings = [bad_meaning, great_meaning, good_meaning]
    
    print(f"good is {good}")
    print(f"good_translate is {good_translate}")
    
    for meaning in meanings:
        if good_translate == meaning:
            print(f"{good_translate} = {meaning}")
        else:
            print(f"{good_translate} != {meaning}")
    
    if good_translate in meanings:
        print(f"good_translate is in meanings")

def test_word_and_regions():
    translator = Translator()
    screen = Screen(OCRAPI(), 'left', Config())
    
    good = Word('good', 'EN')
    good_translate = good.translate('zh-CHS', translator)
    
    rect_example = Rect(Point(0.1, 0.1, screen), Point(0.2, 0.2, screen))
    good_region = Region([Word('好', 'zh-CHS')], rect_example)
    bad_region = Region([Word('坏', 'zh-CHS')], rect_example)
    great_region = Region([Word('极好', 'zh-CHS')], rect_example)
    regions = [bad_region, great_region, good_region]
    
    print(f"good is {good}")
    print(f"good_translate is {good_translate}")
    
    for region in regions:
        if good_translate == region:
            print(f"{good_translate} = {region}")
        else:
            print(f"{good_translate} != {region}")
    
    if good_translate in regions:
        print(f"good_translate is in regions")

def test_ocrapi():
    ocrapi = OCRAPI()
    screenshot_filename = 'sample/screenshot.png'
    
    word_res = ocrapi.ocr(screenshot_filename, 'en')
    meanings_res = ocrapi.ocr(screenshot_filename, 'zh-CHS')
    
    print(word_res)
    print(meanings_res)

def test_screen():
    import time
    screen = Screen(OCRAPI(), 'left', Config())
    
    time.sleep(5)
    word, meanings = screen.ocr()
    
    print(word)
    print(meanings)

if __name__ == "__main__":
    # test_word_and_meanings()
    # test_word_and_regions()
    # test_ocrapi()
    # test_screen()
    pass