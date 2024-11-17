import base64
from collections.abc import Iterable

import requests
import pyautogui

from AuthV3Util import addAuthParams
from util import get_lang, Word, Meaning
from translate import Translator
from main import Config

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

class Screen:
    
    def __init__(self, side: str) -> None:
        self.width, self.height = pyautogui.size()
        self.ocrapi: OCRAPI = OCRAPI()
        self.side: str = side
        self.config = Config(self)

    def click(self, x_ratio: float, y_ratio: float) -> None:
        pyautogui.click(x_ratio*self.width, y_ratio*self.height)
    
    def ocr(self) -> tuple[Word, list['Region']] | None:
        self.screenshot(self.config.word_img_filename, self.get_word_rect())
        self.screenshot(self.config.meanings_img_filename, self.get_meanings_rect())

        word_region = self.ocrapi.ocr(self.config.word_img_filename,
                                      get_lang('ocr', self.config.lang_from))[0]
        if word_region is not None:
            word = Word.from_region_dict(word_region)
        else:
            return None
        
        meanings_region = self.ocrapi.ocr(self.config.meanings_img_filename, get_lang('ocr', self.config.lang_to))
        if meanings_region is not None:
            meanings = [Region.from_region_dict(region, self) for region in meanings_region]
        else:
            return None
        
        return word, meanings

    @staticmethod
    def screenshot(img_filename: str, rect: 'Rect') -> None:
        pyautogui.screenshot(img_filename,
                                (rect.left(),
                                rect.top(),
                                rect.width(),
                                rect.height()
                                )
                             )

    def get_word_rect(self) -> 'Rect':
        if self.side == 'left':
            return self.config.left_word_rect
        elif self.side == 'right':
            return self.config.right_word_rect

    def get_meanings_rect(self) -> 'Rect':
        if self.side == 'left':
            return self.config.left_meanings_rect
        elif self.side == 'right':
            return self.config.right_meanings_rect

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
    
    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x_ratio + other.x_ratio, self.y_ratio + other.y_ratio, self.screen)
    
    def __mul__(self, other) -> 'Point':
        return Point(self.x_ratio * other, self.y_ratio * other, self.screen)
    
    def __truediv__(self, other) -> 'Point':
        return Point(self.x_ratio / other, self.y_ratio / other, self.screen)
    
    def __repr__(self):
        return f"Point({self.x_ratio}, {self.y_ratio})"

class Rect:
    
    def __init__(self, topleft: Point, bottomright: Point):
        self.topleft = topleft
        self.bottomright = bottomright
    
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

    def __repr__(self):
        return f'Rect({self.topleft} {self.bottomright})'

class Region(Meaning):
    def __init__(self, words: Iterable[Word], rect: Rect):
        super().__init__(words)
        self.rect: Rect = rect

    def click(self) -> None:
        self.rect.click()

    @staticmethod
    def from_region_dict(region: dict, screen: Screen) -> 'Region':
        text: str = region['text']
        lang: str = get_lang('ocr_res', region['lang'])
    
        rect: list[str] = region['boundingBox'].split(',')
        topleft = Point(int(rect[0])/screen.width,
                        int(rect[1])/screen.height,
                        screen) + screen.get_meanings_rect().topleft
        bottomright = Point(int(rect[4])/screen.width,
                            int(rect[5])/screen.height,
                            screen) + screen.get_meanings_rect().topleft
        rect: Rect = Rect(topleft, bottomright)
        
        words = map(lambda word: Word(word, lang), text.split(';'))
        return Region(words, rect)

    def __repr__(self):
        return f"Region {self.words}"

def test_word_and_meanings():
    translator = Translator()
    
    good = Word('good', 'en')
    good_translate = good.translate('zh', translator)
    
    good_meaning = Meaning([Word('好', 'zh')])
    bad_meaning = Meaning([Word('坏', 'zh')])
    great_meaning = Meaning([Word('极好', 'zh')])
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
    screen = Screen('left')
    
    good = Word('good', 'en')
    good_translate = good.translate('zh', translator)
    
    rect_example = Rect(Point(0.1, 0.1, screen), Point(0.2, 0.2, screen))
    good_region = Region([Word('好', 'zh')], rect_example)
    bad_region = Region([Word('坏', 'zh')], rect_example)
    great_region = Region([Word('极好', 'zh')], rect_example)
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
    meanings_res = ocrapi.ocr(screenshot_filename, 'zh')
    
    print(word_res)
    print(meanings_res)

def test_screenshot():
    screen = Screen('left')
    Screen.screenshot(screen.config.word_img_filename, screen.get_word_rect())
    Screen.screenshot(screen.config.meanings_img_filename, screen.get_meanings_rect())

def test_screen():
    import time
    screen = Screen('left')
    
    time.sleep(5)
    word, meanings = screen.ocr()
    
    print(word)
    print(meanings)

if __name__ == "__main__":
    # test_word_and_meanings()
    # test_word_and_regions()
    # test_ocrapi()
    # test_screenshot()
    # test_screen()
    pass