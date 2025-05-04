from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WordOption(Base):
    __tablename__ = "word_options"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String)
    is_correct = Column(Boolean)
    sentence_id = Column(Integer, ForeignKey("sentences.id"))
    sentence = relationship("Sentence", back_populates="word_options")

class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    sentence = Column(String)
    tense = Column(String)
    difficulty_level = Column(Integer)
    word_options = relationship("WordOption", back_populates="sentence", cascade="all, delete-orphan")
