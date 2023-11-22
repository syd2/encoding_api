from sqlalchemy import Column, Integer, String

from .database import Base

class Trad(Base):
    __tablename__ = "trads"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(40))
    dictionnary = Column(String(40))
    trad = Column(String(40))
