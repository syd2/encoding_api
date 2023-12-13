from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Trad(Base):
    __tablename__ = "trads"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(40))
    dictionnary = Column(String(40))
    trad = Column(String(40))


class Dict(Base):
    __tablename__ = "dicts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40))
    dict_lines = relationship("DictLine", back_populates="dict")
class DictLine(Base):
    __tablename__ = "dictlines"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(40))
    value = Column(String(40))
    dict_id = Column(Integer, ForeignKey("dicts.id"))
    dict = relationship("Dict", back_populates="dict_lines")