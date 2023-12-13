from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import joinedload

from sqlalchemy import Column, Integer, String, ForeignKey

from .params import TradParams, DictParams, DictLineParams, WordParams
from .response import IndexResponse, getTradResponse, postTradResponse, postDictLine, postDictWithLines, getDictWithLine, postDictResponse, postLinesResponse
from .models import Trad, Dict, Base, DictLine
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

    dict_lines = (
        db.query(DictLine)
        .join(Dict)
        .filter(Dict.name == params.dictionnary)
        .all()
    )


    if not dict_lines:
        raise HTTPException(status_code=404, detail=f"No dictionary found with the name '{params.dictionnary}'.")

    trad = ""
    for char in params.word:
        dict_line = next((line for line in dict_lines if line.key == char), None)
        if dict_line:
            trad += dict_line.value
    trad_db = Trad(word=params.word, trad=trad, dictionnary=params.dictionnary)
    db.add(trad_db)
    db.commit()

    return {
        'word': params.word,
        'dictionnary': params.dictionnary,
        'trad': trad
    }



@app.post("/trad_word", response_model=getTradResponse)
def get_word_by_trad(params: WordParams, db: Session = Depends(get_db)):
    dict_lines = (
        db.query(DictLine)
        .join(Dict)
        .filter(Dict.name == params.dictionary)
        .all()
    )

    encoded_to_key = {line.value: line.key for line in dict_lines}
    decoded_word = "".join(encoded_to_key.get(char, char) for char in params.trad)

    return {
        'word': decoded_word,
        'dictionnary': params.dictionary,
        'trad': params.trad
    }



@app.get("/trad/{word}", response_model=getTradResponse)
def trad(word: str, db: Session = Depends(get_db)):
    trad = db.query(Trad).filter(Trad.word == word).first()

    if trad is None:
        raise HTTPException(status_code=404, detail="Translation not found")

    return getTradResponse(word=trad.trad)


@app.post('/dict', response_model=postDictResponse)
def postDict(params: DictParams, db: Session = Depends(get_db)):
    dict_db = Dict(name=params.name)
    db.add(dict_db)
    return dict_db


@app.post("/dicts", response_model=postDictWithLines)
def create_dict_with_lines(dict_data: postDictWithLines, db: Session = Depends(get_db)):

    dict = Dict(name=dict_data.name)
    db.add(dict)
    db.commit()
    db.refresh(dict)

    # Create dict lines
    lines = []
    for line_data in dict_data.lines:
        dict_line = DictLine(key=line_data.key, value=line_data.value, dict_id=dict.id)
        db.add(dict_line)
        db.commit() 
        db.refresh(dict_line)
        lines.append(postDictLine(id=dict_line.id, key=dict_line.key, value=dict_line.value, dict_id=dict_line.dict_id))

    db.commit()

    return postDictWithLines(name=dict_data.name, lines=lines)

#prendre tout les dictionaire
@app.get("/dicts", response_model=list[getDictWithLine])
def get_dictionaries(db: Session = Depends(get_db)):
    dictionaries = db.query(Dict).all()
    dictionaries_response = [
        getDictWithLine(
            id=dictionary.id,
            name=dictionary.name,
            lines=[postDictLine(id=line.id, key=line.key, value=line.value, dict_id=line.dict_id) for line in dictionary.dict_lines]
        )
        for dictionary in dictionaries
    ]

    return dictionaries_response


@app.put("/dicts/{dict_id}", response_model=postDictWithLines)
def update_dict(dict_id: int, dict_data: postDictWithLines, db: Session = Depends(get_db)):

    dictionary = db.query(Dict).filter(Dict.id == dict_id).first()
    if not dictionary:
        raise HTTPException(status_code=404, detail=f"Dictionary with id {dict_id} not found.")

    dictionary.name = dict_data.name
    db.commit()
    db.refresh(dictionary)
    db.query(DictLine).filter(DictLine.dict_id == dict_id).delete()
    lines = []
    for line_data in dict_data.lines:
        dict_line = DictLine(key=line_data.key, value=line_data.value, dict_id=dictionary.id)
        db.add(dict_line)
        db.commit()
        db.refresh(dict_line)
        lines.append(postDictLine(id=dict_line.id, key=dict_line.key, value=dict_line.value, dict_id=dict_line.dict_id))

    return postDictWithLines(id=dictionary.id, name=dictionary.name, lines=lines)


@app.delete("/dicts/{dict_id}", response_model=postDictWithLines)
def delete_dict(dict_id: int, db: Session = Depends(get_db)):

    dictionary = db.query(Dict).filter(Dict.id == dict_id).first()
    if not dictionary:
        raise HTTPException(status_code=404, detail=f"Dictionary with id {dict_id} not found.")

    lines = db.query(DictLine).filter(DictLine.dict_id == dict_id).all()

    db.query(DictLine).filter(DictLine.dict_id == dict_id).delete()
    db.delete(dictionary)
    db.commit()

    return postDictWithLines(
            name=dictionary.name,
            lines=[postDictLine(id=line.id, key=line.key, value=line.value, dict_id=line.dict_id) for line in dictionary.dict_lines]
        )







#prendre un dictionaire par son nom
@app.get("/dict/{name}", response_model=getDictWithLine)
def getDict(name: str, db: Session = Depends(get_db)):
    dict = db.query(Dict).filter(Dict.name == name).first()
    if dict is None:
        raise HTTPException(status_code=404, detail="dictionary not found")
    dict_res = getDictWithLine(
            id=dict.id,
            name=dict.name,
            lines=[postDictLine(id=line.id, key=line.key, value=line.value, dict_id=line.dict_id) for line in dict.dict_lines]
        )
    return dict_res




@app.post("/dict/{dict_id}/lines", response_model=postLinesResponse)
def post_dictline(dict_id: int, params: DictLineParams,  db: Session = Depends(get_db)):

    dict = db.query(Dict).filter(Dict.id == dict_id).first()
    if not dict:
        raise HTTPException(status_code=404, detail=f"dictionary with id {dict_id} not found.")

    dict_line = DictLine(key=params.key, value=params.value, dict_id=dict_id)
    db.add(dict_line)
    db.commit()
    db.refresh(dict_line)

    return dict_line