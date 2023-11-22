from pydantic import BaseModel

class TradParams(BaseModel):
    word: str
    dictionnary: str