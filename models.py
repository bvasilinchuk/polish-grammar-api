from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from datetime import timedelta

Base = declarative_base()

class Theme(Base):
    __tablename__ = "themes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    parent_theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('name', 'parent_theme_id', name='uix_theme_name_parent'),
    )

    parent_theme = relationship("Theme", remote_side=[id])
    subthemes = relationship("Theme", back_populates="parent_theme", cascade="all, delete-orphan")
    sentences = relationship("Sentence", back_populates="theme", cascade="all, delete-orphan")
    user_progress = relationship("UserProgress", back_populates="theme", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Theme(id={self.id}, name='{self.name}', parent_theme_id={self.parent_theme_id})"

    def get_next_sentence(self, user_id: int) -> Optional['Sentence']:
        from database import SessionLocal
        db = SessionLocal()
        try:
            progress = db.query(UserProgress).filter_by(user_id=user_id, theme_id=self.id).first()
            if not progress:
                return self.sentences[0] if self.sentences else None
            next_index = progress.current_sentence_index
            if next_index >= len(self.sentences):
                return None
            return self.sentences[next_index]
        finally:
            db.close()

    def update_progress(self, user_id: int, sentence: 'Sentence') -> None:
        from database import SessionLocal
        db = SessionLocal()
        try:
            progress = db.query(UserProgress).filter_by(user_id=user_id, theme_id=self.id).first()
            if not progress:
                progress = UserProgress(
                    user_id=user_id,
                    theme_id=self.id,
                    current_sentence_index=0,
                    completed_sentences=0
                )
                db.add(progress)
            progress.current_sentence_index = self.sentences.index(sentence) + 1
            progress.completed_sentences += 1
            progress.last_accessed = datetime.utcnow()
            db.commit()
        finally:
            db.close()

    def get_all_subthemes(self) -> List['Theme']:
        subthemes = []
        for subtheme in self.subthemes:
            subthemes.append(subtheme)
            subthemes.extend(subtheme.get_all_subthemes())
        return subthemes

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"User(id={self.id}, email='{self.email}')"

class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    theme_id = Column(Integer, ForeignKey("themes.id"))
    current_sentence_index = Column(Integer, default=0)
    completed_sentences = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress")
    theme = relationship("Theme", back_populates="user_progress")
    
    __table_args__ = (UniqueConstraint('user_id', 'theme_id', name='_user_theme_uc'),)
    
    def __repr__(self):
        return f"UserProgress(id={self.id}, user_id={self.user_id}, theme_id={self.theme_id}, completed={self.completed_sentences})"

class WordOption(Base):
    __tablename__ = "word_options"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    word = Column(String)
    is_correct = Column(Boolean)
    sentence_id = Column(Integer, ForeignKey("sentences.id"))
    sentence = relationship("Sentence", back_populates="word_options")

class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    sentence = Column(String, index=True)
    tense = Column(String)
    difficulty_level = Column(Integer)
    theme_id = Column(Integer, ForeignKey("themes.id"))
    order_in_theme = Column(Integer, nullable=False)
    theme = relationship("Theme", back_populates="sentences")
    word_options = relationship("WordOption", back_populates="sentence", cascade="all, delete-orphan")

# Pydantic models for API requests and responses
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        orm_mode = True

class WordOptionResponse(BaseModel):
    unique_id: str
    word: str
    is_correct: bool

class SentenceCreate(BaseModel):
    sentence: str
    tense: str
    difficulty_level: int
    word_options: List[WordOptionResponse]
    theme_id: int
    order_in_theme: int

class SentenceResponse(BaseModel):
    id: int
    sentence: str
    tense: str
    difficulty_level: int
    word_options: List[WordOptionResponse]
    theme_id: int
    order_in_theme: int
    
    class Config:
        orm_mode = True

class ThemeCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ThemeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    total_sentences: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProgressResponse(BaseModel):
    id: int
    theme_id: int
    current_sentence_index: int
    completed_sentences: int
    last_accessed: datetime
    
    class Config:
        orm_mode = True
