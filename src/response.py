from pydantic import BaseModel

class IndexResponse(BaseModel):
    msg: str

class getTradResponse(BaseModel):
    word: str

class postTradResponse(BaseModel):
    word: str
    dictionnary: str
    trad: str