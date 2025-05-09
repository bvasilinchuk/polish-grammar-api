from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import random
import uuid

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

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///polish_grammar.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- User Model for Account Management ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    tense = Column(String)      # e.g., "perfective", "imperfective"
    difficulty_level = Column(Integer)
    word_options = relationship("WordOption", back_populates="sentence", cascade="all, delete-orphan")

Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
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

class SentenceResponse(BaseModel):
    id: int
    sentence: str
    tense: str
    difficulty_level: int
    word_options: List[WordOptionResponse]

# --- Auth and Security Utilities ---
SECRET_KEY = "supersecretkey123"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    db = SessionLocal()
    user = get_user_by_email(db, token_data.email)
    db.close()
    if user is None:
        raise credentials_exception
    return user

# --- User Registration Endpoint ---
@app.post("/api/register", response_model=Token)
def register(user: UserCreate):
    db = SessionLocal()
    db_user = get_user_by_email(db, user.email)
    if db_user:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": user.email})
    db.close()
    return {"access_token": access_token, "token_type": "bearer"}

# --- User Login Endpoint ---
@app.post("/api/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Pydantic Schemas for User Management ---
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
class SentenceResponse(BaseModel):
    id: int
    sentence: str
    tense: str
    difficulty_level: int
    word_options: List[WordOptionResponse]



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
        
        # Convert SQLAlchemy objects to Pydantic models
        word_option_responses = [
            WordOptionResponse(
                unique_id=opt.unique_id,
                word=opt.word,
                is_correct=opt.is_correct
            ) for opt in word_options
        ]
        
        return SentenceResponse(
            id=random_sentence.id,
            sentence=random_sentence.sentence,
            tense=random_sentence.tense,
            difficulty_level=random_sentence.difficulty_level,
            word_options=word_option_responses
        )
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
    # Do not run uvicorn here; Railway will start the server using the external command.
