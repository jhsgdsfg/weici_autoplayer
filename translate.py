import requests

from AuthV3Util import addAuthParams

class Translator:
    
    def __init__(self) -> None:
        self.query_url = "https://openapi.youdao.com/api"
        self.appkey = "157438dc01f55c58"
        self.key = "fz1VVcsGrhoWtiqqehASiJz1SvSxQlTp"
    
    def translate(self,
                  text: str,
                  src: str,
                  dst: str) -> list[str]:
        
        data = {'q': text, 'from': src, 'to': dst}

        addAuthParams(self.appkey, self.key, data)

        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        res = requests.post(self.query_url,
                            data,
                            header).json()
        
        return res['translation']
