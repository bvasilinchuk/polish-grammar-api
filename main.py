from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import random

app = FastAPI(
    title="Polish Grammar API",
    description="API for Polish grammar learning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///polish_grammar.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
    sentence = Column(String, index=True)
    tense = Column(String)      # e.g., "perfective", "imperfective"
    difficulty_level = Column(Integer)
    word_options = relationship("WordOption", back_populates="sentence", cascade="all, delete-orphan")

Base.metadata.create_all(bind=engine)

class WordOptionResponse(BaseModel):
    word: str
    is_correct: bool

class SentenceCreate(BaseModel):
    sentence: str
    tense: str
    difficulty_level: int
    word_options: List[WordOptionResponse]

class SentenceResponse(BaseModel):
    id: int
    sentence: str
    tense: str
    difficulty_level: int
    word_options: List[WordOptionResponse]

class SentenceVerify(BaseModel):
    sentence_id: int
    selected_word: str

@app.get("/web")
async def database_viewer(request: Request):
    db = SessionLocal()
    try:
        sentences = db.query(Sentence).all()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "sentences": sentences
        })
    finally:
        db.close()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/sentences/random", response_model=SentenceResponse)
async def get_random_sentence():
    db = SessionLocal()
    try:
        # Get all sentences and select a random one
        sentences = db.query(Sentence).all()
        if not sentences:
            raise HTTPException(status_code=404, detail="No sentences available")
        
        random_sentence = random.choice(sentences)
        # Randomize the order of word options
        word_options = random_sentence.word_options
        random.shuffle(word_options)
        
        return {
            "id": random_sentence.id,
            "sentence": random_sentence.sentence,
            "tense": random_sentence.tense,
            "difficulty_level": random_sentence.difficulty_level,
            "word_options": word_options
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/sentences/verify", response_model=SentenceResponse)
async def verify_answer(sentence_verify: SentenceVerify):
    db = SessionLocal()
    try:
        sentence = db.query(Sentence).filter(Sentence.id == sentence_verify.sentence_id).first()
        if not sentence:
            raise HTTPException(status_code=404, detail="Sentence not found")
        
        # Find the selected word in the options
        selected_option = next((opt for opt in sentence.word_options 
                              if opt.word.lower() == sentence_verify.selected_word.lower()), None)
        
        if not selected_option:
            raise HTTPException(status_code=400, detail="Invalid word selection")
            
        if selected_option.is_correct:
            return sentence
        else:
            raise HTTPException(status_code=400, detail="Incorrect answer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/sentences", response_model=SentenceResponse)
async def create_sentence(sentence: SentenceCreate):
    db = SessionLocal()
    try:
        db_sentence = Sentence(**sentence.dict())
        db.add(db_sentence)
        db.commit()
        db.refresh(db_sentence)
        return db_sentence
    finally:
        db.close()

def init_db():
    db = SessionLocal()
    try:
        # Add some sample sentences
        sample_sentences = [
            {
                "sentence": "On _____ (jeść) obiad.",
                "correct_answer": "je",  # present tense, 3rd person singular
                "verb_form": "present",
                "tense": "imperfective",
                "difficulty_level": 1
            },
            {
                "sentence": "Oni _____ (pójść) do szkoły.",
                "correct_answer": "idą",  # present tense, 3rd person plural
                "verb_form": "present",
                "tense": "imperfective",
                "difficulty_level": 1
            },
            {
                "sentence": "On _____ (pójść) do domu wczoraj.",
                "correct_answer": "poszedł",  # past tense, 3rd person singular
                "verb_form": "past",
                "tense": "perfective",
                "difficulty_level": 2
            }
        ]

        # Add sentences to database if they don't exist
        existing_sentences = db.query(Sentence).count()
        if existing_sentences == 0:
            for sentence_data in sample_sentences:
                sentence = Sentence(**sentence_data)
                db.add(sentence)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
