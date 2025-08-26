from tkinter import CASCADE
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# modelos orm sqlalchemy dos paises
class countries(Base):
    __tablename__  = "countries"
    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, index=True) # nome do país, indexado para buscas otimizadas
    likes = Column(Integer, default=0) # número de likes, padrão 0
    dislikes = Column(Integer, default=0) # número de dislikes, padrão 0