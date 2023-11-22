from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .params import TradParams
from .response import IndexResponse, getTradResponse, postTradResponse
from .models import Trad, Base
from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=IndexResponse)
def index():
    return {'msg': 'Hello World !'}

@app.post('/trad', response_model=postTradResponse)
def postTrad(params: TradParams, db: Session = Depends(get_db)):

    trad = "... --- ..."

    trad_db = Trad(word=params.word, trad=trad, dictionnary=params.dictionnary)
    db.add(trad_db)
    db.commit()

    return {
        'word': params.word,
        'dictionnary': params.dictionnary,
        'trad': trad
    }

@app.get("/trad/{word}", response_model=getTradResponse)
def trad(word: str):
    return {
        'word': word
    }