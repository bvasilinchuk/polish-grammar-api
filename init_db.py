from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Sentence

# Create the database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./polish_grammar.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Add more diverse Polish sentences
sample_sentences = [
    {
        "sentence": "On ___________ (jeść) obiad.",
        "verb_form": "je",
        "tense": "present",
        "difficulty_level": 1
    },
    {
        "sentence": "Wczoraj oni ___________ (iść) do szkoły.",
        "verb_form": "szli",
        "tense": "past",
        "difficulty_level": 2
    },
    {
        "sentence": "Ona ___________ (być) w domu.",
        "verb_form": "jest",
        "tense": "present",
        "difficulty_level": 1
    },
    {
        "sentence": "Oni ___________ (móc) pomóc.",
        "verb_form": "mogą",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "On ___________ (piec) ciasto.",
        "verb_form": "piecze",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "My ___________ (czytać) książkę.",
        "verb_form": "czytamy",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "Ona ___________ (płakać) wczoraj.",
        "verb_form": "plakała",
        "tense": "past",
        "difficulty_level": 2
    },
    {
        "sentence": "Oni ___________ (być) zadowoleni.",
        "verb_form": "są",
        "tense": "present",
        "difficulty_level": 1
    },
    {
        "sentence": "On ___________ (piec) ciasto.",
        "verb_form": "piecze",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "My ___________ (piec) ciasto.",
        "verb_form": "pieczemy",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "Oni ___________ (piec) ciasto.",
        "verb_form": "pieczą",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "Ona ___________ (piec) ciasto.",
        "verb_form": "piecze",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "On ___________ (piec) ciasto.",
        "verb_form": "piecze",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "My ___________ (piec) ciasto.",
        "verb_form": "pieczemy",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "Oni ___________ (piec) ciasto.",
        "verb_form": "pieczą",
        "tense": "present",
        "difficulty_level": 2
    },
    {
        "sentence": "Ona ___________ (piec) ciasto.",
        "verb_form": "piecze",
        "tense": "present",
        "difficulty_level": 2
    }
]

# First delete all existing sentences
db.query(Sentence).delete()

# Add sample sentences to the database
for sentence_data in sample_sentences:
    sentence = Sentence(**sentence_data)
    db.add(sentence)

db.commit()
db.close()
