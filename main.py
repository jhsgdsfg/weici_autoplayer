import pyautogui

from translate import Translator
from ocr import OCR

class ScreenShot:
    
    def __init__(self, ocr: OCR) -> None:
        self.img = pyautogui.screenshot()
        self.ocr: OCR = ocr
    
    def ocr(self) -> tuple["Word", list["Meaning"]]:
        self.ocr.ocr(self.img)
    
class Word:
    
    def __init__(self,
                 text: str,
                 lang: str,
                 translator: "Translator") -> None:
        self.text: str = text
        self.lang: str = lang
        self.translator: Translator = translator
    
    def translate(self, target: str) -> "Meaning":
        res = self.translator.translate(self.text,
                                        self.lang,
                                        target)
        
        words = []
        for word in res:
            word = Word(word, target, self.translator)
            words.append(word)
        
        return Meaning(words)
    
    def __repr__(self):
        return f"Word {self.text} in {self.lang}"
    
    def __eq__(self, value: "Word") -> bool:
        return self.text == value.text
    
class Meaning:
    
    def __init__(self, words: list[Word]) -> None:
        self.words: list[Word] = words
    
    def __repr__(self):
        return f"Meaning {self.words}"
    
    def __eq__(self, value: "Meaning") -> bool:
        for word in self.words:
            if word in value.words:
                return True
        return False
    

def main():
    translator = Translator()
    
    good = Word('good', 'EN', translator)
    good_translate = good.translate('zh-CHS')
    
    good_meaning = Meaning([Word('好', 'zh-CHS', translator)])
    bad_meaning = Meaning([Word('坏', 'zh-CHS', translator)])
    great_meaning = Meaning([Word('极好', 'zh-CHS', translator)])
    meanings = [bad_meaning, great_meaning, good_meaning]
    
    print(f"good is {good}")
    print(f"good_translate is {good_translate}")
    
    for meaning in meanings:
        if good_translate == meaning:
            print(f"{good_translate} = {meaning}")
        else:
            print(f"{good_translate} != {good_meaning}")
    
    if good_translate in meanings:
        print(f"good_translate is in meanings")

if __name__ == "__main__":
    main()