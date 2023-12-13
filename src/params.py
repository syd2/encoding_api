from pydantic import BaseModel

class TradParams(BaseModel):
    word: str
    dictionnary: str

class DictParams(BaseModel):
    name: str

class DictLineParams(BaseModel):
    key: str
    value: str

class WordParams(BaseModel):
    trad: str
    dictionary: str