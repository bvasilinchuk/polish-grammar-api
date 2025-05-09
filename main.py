from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload, sessionmaker, declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid
import logging
import random

from database import get_db, engine, Base
from models import (
    Theme,
    Sentence,
    WordOption,
    UserProgress,
    User,
    UserCreate,
    UserLogin,
    Token,
    TokenData,
    RegisterResponse,
    UserResponse,
    WordOptionResponse,
    SentenceCreate,
    SentenceResponse,
    ThemeCreate,
    ThemeResponse,
    UserProgressResponse
)

app = FastAPI(
    title="Polish Grammar API",
    description="API for Polish Grammar learning app",
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# All models are imported from models.py - no need to define them here

# Ensure database tables are created
print("Initializing database tables...")

# First try direct SQLite initialization
import subprocess
import os

try:
    print("Running direct SQLite initialization script...")
    # Check if the script exists
    if os.path.exists("init_railway_db.py"):
        result = subprocess.run(["python", "init_railway_db.py"], capture_output=True, text=True)
        print(f"Initialization script output: {result.stdout}")
        if result.stderr:
            print(f"Initialization script errors: {result.stderr}")
    else:
        print("Initialization script not found, falling back to SQLAlchemy")
        
    # Also try SQLAlchemy initialization as a backup
    from models import User, Theme, Sentence, WordOption, UserProgress  # Import all models to ensure they're registered
    Base.metadata.create_all(bind=engine)
    print("SQLAlchemy tables created successfully")
    
    # Try to create a test user if needed
    db = SessionLocal()
    try:
        # Try to get user count
        try:
            user_count = db.query(User).count()
            print(f"Found {user_count} users in database")
            
            # If no users, create a test user
            if user_count == 0:
                print("Creating test user...")
                hashed_password = pwd_context.hash("Qwerty12")
                test_user = User(
                    email="test1@mail.ru",
                    hashed_password=hashed_password,
                    created_at=datetime.utcnow()
                )
                db.add(test_user)
                db.commit()
                print("Test user created successfully")
        except Exception as e:
            print(f"Error checking users: {str(e)}")
    finally:
        db.close()
except Exception as e:
    print(f"Error during database initialization: {str(e)}")
    
print("Database initialization complete")

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
# Using models from models.py

@app.post("/api/register", response_model=RegisterResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, created_at=datetime.utcnow())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RegisterResponse(id=db_user.id, email=db_user.email)

# --- User Login Endpoint ---
@app.post("/api/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        print(f"Login attempt for email: {login_data.email}")
        
        # Get the user from the database
        db_user = get_user_by_email(db, login_data.email)
        print(f"User found: {db_user is not None}")
        
        if not db_user:
            print("User not found, raising 401")
            raise HTTPException(status_code=401, detail="User not found")
        
        # Verify the password
        password_valid = verify_password(login_data.password, db_user.hashed_password)
        print(f"Password valid: {password_valid}")
        
        if not password_valid:
            print("Password invalid, raising 401")
            raise HTTPException(status_code=401, detail="Incorrect password")
        
        # Create and return the access token
        print("Creating access token")
        access_token = create_access_token(data={"sub": db_user.email})
        print("Access token created successfully")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error in login endpoint: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

# --- Theme Management Endpoints ---
@app.get("/api/themes", response_model=List[ThemeResponse])
def get_themes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all main themes and their subthemes, with sentence counts and user progress."""
    try:
        print(f"Fetching themes for user: {current_user.email}")
        
        # Get all main themes (those without a parent)
        print("Querying main themes")
        main_themes = db.query(Theme).filter(Theme.parent_theme_id.is_(None)).all()
        print(f"Found {len(main_themes)} main themes")
        
        response = []
        for theme in main_themes:
            print(f"Processing theme: {theme.id} - {theme.name}")
            
            # Get user progress for this theme
            print(f"Querying progress for user {current_user.id} and theme {theme.id}")
            progress = db.query(UserProgress).filter_by(user_id=current_user.id, theme_id=theme.id).first()
            completed = progress.completed_sentences if progress else 0
            print(f"Completed sentences: {completed}")
            
            # Get sentence count
            sentence_count = len(theme.sentences)
            print(f"Total sentences: {sentence_count}")
            
            # Build response object
            theme_response = {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "total_sentences": sentence_count,
                "completed_sentences": completed,
                "created_at": theme.created_at,
                "updated_at": theme.updated_at
            }
            response.append(theme_response)
            print(f"Added theme to response: {theme.name}")
        
        print(f"Returning {len(response)} themes")
        return response
    except Exception as e:
        print(f"Error in get_themes endpoint: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

@app.get("/api/themes/{theme_id}/subthemes", response_model=List[ThemeResponse])
def get_subthemes(theme_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all subthemes for a specific theme, including correct total_sentences and user progress."""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    subthemes = theme.get_all_subthemes()
    response = []
    for subtheme in subthemes:
        progress = db.query(UserProgress).filter_by(user_id=current_user.id, theme_id=subtheme.id).first()
        completed = progress.completed_sentences if progress else 0
        response.append({
            "id": subtheme.id,
            "name": subtheme.name,
            "description": subtheme.description,
            "total_sentences": len(subtheme.sentences),
            "completed_sentences": completed,
            "created_at": subtheme.created_at,
            "updated_at": subtheme.updated_at
        })
    return response

@app.get("/api/themes/{theme_id}/sentences", response_model=List[SentenceResponse])
def get_theme_sentences(theme_id: int, db: Session = Depends(get_db)):
    """Get all sentences for a theme or subtheme."""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme.sentences

@app.get("/api/themes/{theme_id}/progress", response_model=UserProgressResponse)
def get_theme_progress(theme_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user progress for a theme or subtheme."""
    progress = db.query(UserProgress).filter_by(user_id=current_user.id, theme_id=theme_id).first()
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this theme")
    return progress

@app.get("/api/themes/{theme_id}/next_sentence", response_model=SentenceResponse)
def get_next_sentence(theme_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the next sentence for the user in the theme/subtheme."""
    try:
        # Step 1: Get the theme
        theme = db.query(Theme).filter(Theme.id == theme_id).first()
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
            
        # Step 2: Get all sentences for this theme
        sentences = db.query(Sentence).filter(Sentence.theme_id == theme_id).order_by(Sentence.order_in_theme).all()
        if not sentences:
            raise HTTPException(status_code=404, detail="No sentences in this theme")
            
        # Step 3: Get user progress
        progress = db.query(UserProgress).filter_by(user_id=current_user.id, theme_id=theme_id).first()
        next_index = progress.current_sentence_index if progress else 0
        
        # Step 4: Validate index
        if next_index < 0:
            next_index = 0
        if next_index >= len(sentences):
            raise HTTPException(status_code=404, detail="No more sentences left in this theme")
            
        # Step 5: Get the next sentence
        sentence = sentences[next_index]
        
        # Step 6: Get word options separately
        word_options = db.query(WordOption).filter(WordOption.sentence_id == sentence.id).all()
        
        # Step 7: Create the response
        return {
            "id": sentence.id,
            "sentence": sentence.sentence,
            "tense": sentence.tense,
            "difficulty_level": sentence.difficulty_level,
            "word_options": [
                {
                    "unique_id": opt.unique_id,
                    "word": opt.word,
                    "is_correct": opt.is_correct
                } for opt in word_options
            ],
            "theme_id": sentence.theme_id,
            "order_in_theme": sentence.order_in_theme
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logging.error(f"Full traceback for get_next_sentence error: {tb}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/api/progress")
def update_progress(theme_id: int, sentence_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user progress after completing a sentence."""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id, Sentence.theme_id == theme_id).first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found in this theme")
    progress = db.query(UserProgress).filter_by(user_id=current_user.id, theme_id=theme_id).first()
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            theme_id=theme_id,
            current_sentence_index=1,
            completed_sentences=1,
            last_accessed=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.current_sentence_index += 1
        progress.completed_sentences += 1
        progress.last_accessed = datetime.utcnow()
    db.commit()
    return {"status": "success"}

@app.get("/api/themes/{theme_id}/subthemes", response_model=List[ThemeResponse])
def get_subthemes(theme_id: int, db: Session = Depends(get_db)):
    """Get all subthemes for a specific theme, including correct total_sentences."""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    subthemes = theme.get_all_subthemes()
    response = []
    for subtheme in subthemes:
        response.append(
            ThemeResponse(
                id=subtheme.id,
                name=subtheme.name,
                description=subtheme.description,
                total_sentences=len(subtheme.sentences),
                created_at=subtheme.created_at,
                updated_at=subtheme.updated_at
            )
        )
    return response

@app.post("/api/themes", response_model=ThemeResponse)
def create_theme(theme: ThemeCreate, db: Session = Depends(get_db)):
    db_theme = Theme(**theme.dict())
    db.add(db_theme)
    db.commit()
    db.refresh(db_theme)
    return db_theme

@app.get("/api/user/progress", response_model=List[UserProgressResponse])
def get_user_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get progress for all themes for the current user."""
    return db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    password: str

# All models are imported from models.py
# All models are imported from models.py



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
    """Initialize the database with themes and subthemes."""
    db = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create main themes
        cases = Theme(
            name="Cases",
            description="Practice Polish cases",
            created_at=datetime.utcnow()
        )
        
        verb_conjugation = Theme(
            name="Verb Conjugation",
            description="Practice verb conjugation",
            created_at=datetime.utcnow()
        )
        
        aspect = Theme(
            name="Aspect of Verbs",
            description="Practice verb aspects",
            created_at=datetime.utcnow()
        )
        
        plural_forms = Theme(
            name="Plural Forms and Usage",
            description="Practice plural forms",
            created_at=datetime.utcnow()
        )
        
        pronouns = Theme(
            name="Pronouns",
            description="Practice pronouns",
            created_at=datetime.utcnow()
        )
        
        particles = Theme(
            name="Particles and Prepositions",
            description="Practice particles and prepositions",
            created_at=datetime.utcnow()
        )
        
        complex_sentences = Theme(
            name="Complex Sentences",
            description="Practice complex sentence structures",
            created_at=datetime.utcnow()
        )
        
        question_structures = Theme(
            name="Question Structures",
            description="Practice question formations",
            created_at=datetime.utcnow()
        )
        
        # Add main themes first
        db.add_all([
            cases, verb_conjugation, aspect, plural_forms, pronouns,
            particles, complex_sentences, question_structures
        ])
        db.commit()  # Commit to get IDs
        
        # Add subthemes with proper parent IDs
        cases_subthemes = [
            Theme(
                name="Nominative",
                description="Practice nominative case",
                parent_theme_id=cases.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Genitive",
                description="Practice genitive case",
                parent_theme_id=cases.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Dative",
                description="Practice dative case",
                parent_theme_id=cases.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Accusative",
                description="Practice accusative case",
                parent_theme_id=cases.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Instrumental",
                description="Practice instrumental case",
                parent_theme_id=cases.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Locative",
                description="Practice locative case",
                parent_theme_id=cases.id,
                created_at=datetime.utcnow()
            )
        ]
        
        verb_conjugation_subthemes = [
            Theme(
                name="Present",
                description="Practice present tense",
                parent_theme_id=verb_conjugation.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Past",
                description="Practice past tense",
                parent_theme_id=verb_conjugation.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Future",
                description="Practice future tense",
                parent_theme_id=verb_conjugation.id,
                created_at=datetime.utcnow()
            )
        ]
        
        aspect_subthemes = [
            Theme(
                name="Perfective",
                description="Practice perfective aspect",
                parent_theme_id=aspect.id,
                created_at=datetime.utcnow()
            ),
            Theme(
                name="Imperfective",
                description="Practice imperfective aspect",
                parent_theme_id=aspect.id,
                created_at=datetime.utcnow()
            )
        ]
        
        # Add subthemes
        db.add_all([
            *cases_subthemes, *verb_conjugation_subthemes, *aspect_subthemes
        ])
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
