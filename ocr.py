import base64

import requests
import pyautogui

from AuthV3Util import addAuthParams

class OCR:

    def __init__(self) -> None:
        self.imgfile = open('screenshot.jpg', 'rb')
        self.query_url = "https://openapi.youdao.com/ocrapi"
        self.appkey = "157438dc01f55c58"
        self.key = "fz1VVcsGrhoWtiqqehASiJz1SvSxQlTp"
        self.lang_type = 'auto'
        self.detect_type = '10012'
        self.image_type = '1'
        self.doc_type = 'json'
  
    def ocr(self, img) -> list["Region"]:

        # < 8mb
        # TODO: convert image to base64
        img = str(base64.b64encode(self.imgfile.read()), 'utf-8')
        
        data = {'img': img,
                'langType': self.lang_type,
                'detectType': self.detect_type,
                'imageType': self.image_type,
                'docType': self.doc_type,
                }

        addAuthParams(self.appkey, self.key, data)

        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        res =  requests.post(self.query_url, data, header).json()
        
        regions = map(Region.from_region_dict, res['regions'])
        
        return regions
        
        
class Screen:
    def __init__(self):
        self.size: tuple[int, int] = pyautogui.
    
    def click(self, x_ratio: float, y_ratio: float) -> None:
        pyautogui.click()

class Point:
    
    def __init__(self,
                 x_ratio: float,
                 y_ratio: float,
                 screen: Screen) -> None:
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.screen = screen
    
    def click(self)
    
    def __add__(self, value: "Point") -> "Point":
        return Point(self.x+value.x, self.y+value.y)
    
    def __mul__(self, value) -> "Point":
        return Point(self.x*value, self.y*value)
    
    def __div__(self, value) -> "Point":
        return Point(self.x/value, self.y/value)
    
    def __repr__(self):
        return f"Point ({self.x}, {self.y})"

class Rect:
    
    def __init__(self, upleft: Point, downright: Point):
        self.upleft = upleft
        self.downright = downright
    
    def center(self) -> Point:
        return (self.upleft + self.downright) / 2

class Region:
    def __init__(self,
                 text: str,
                 bounding_box: tuple[Point, Point]):
        self.text = text
        # upleft and downright
        self.bounding_box = bounding_box
    
    def center(self) -> Point:
        return (self.bounding_box[0] + self.bounding_box[1]) / 2
    
    @staticmethod
    def from_region_dict(region: dict) -> "Region":
        bounding_box: str = region['boundingBox']
        bounding_box: list[str] = bounding_box.split(',')
        bounding_box = [Point(int(bounding_box[0]), int(bounding_box[1])),
                        Point(int(bounding_box[4]), int(bounding_box[5]))]
        
        text = region['text']
        lang = region['lang']
        
        return Region(text, bounding_box)
    
    def __repr__(self):
        return f"Region {self.text} at {self.bounding_box}"


def test():
    from PIL import Image
    ocr = OCR()
    print(ocr.ocr(Image.open("screenshot.jpg")))
    
if __name__ == "__main__":
    test()