from pydantic import BaseModel
from typing import List

class IndexResponse(BaseModel):
    msg: str

class getTradResponse(BaseModel):
    word: str

class postTradResponse(BaseModel):
    word: str
    dictionnary: str
    trad: str


class postDictLine(BaseModel):
    id: int
    key: str
    value: str

class getDictWithLine(BaseModel):
    id: int
    name: str
    lines: List[postDictLine]

class postDictWithLines(BaseModel):
    name : str
    lines : List[postDictLine]


class postDictResponse(BaseModel):
    name: str


# class getDictLineResponse(BaseModel):
#     key: str
#     value: str
#     dict_id: int


#post only line in a dict
class postLinesResponse(BaseModel):
    key: str
    value: str
    dict_id: int
