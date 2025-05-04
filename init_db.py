import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Sentence, WordOption

# Create the database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./polish_grammar.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Add more diverse Polish sentences with multiple choice options
sample_sentences = [
    {
        "sentence": "On ___________ (jeść) obiad.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "je", "is_correct": True},
            {"word": "jedzie", "is_correct": False},
            {"word": "jedł", "is_correct": False},
            {"word": "jedziemy", "is_correct": False}
        ]
    },
    {
        "sentence": "Wczoraj oni ___________ (iść) do szkoły.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "szli", "is_correct": True},
            {"word": "szedł", "is_correct": False},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False}
        ]
    },
    {
        "sentence": "Ona ___________ (być) w domu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "jest", "is_correct": True},
            {"word": "była", "is_correct": False},
            {"word": "są", "is_correct": False},
            {"word": "był", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___________ (móc) pomóc.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "mogą", "is_correct": True},
            {"word": "mogę", "is_correct": False},
            {"word": "mogli", "is_correct": False},
            {"word": "mogę", "is_correct": False}
        ]
    },
    {
        "sentence": "On ___________ (piec) ciasto.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "piecze", "is_correct": True},
            {"word": "piecze", "is_correct": False},
            {"word": "piecą", "is_correct": False},
            {"word": "pieczemy", "is_correct": False}
        ]
    },
    {
        "sentence": "My ___________ (czytać) książkę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "czytamy", "is_correct": True},
            {"word": "czyta", "is_correct": False},
            {"word": "czytają", "is_correct": False},
            {"word": "czytał", "is_correct": False}
        ]
    },
    {
        "sentence": "Ona ___________ (płakać) wczoraj.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "plakała", "is_correct": True},
            {"word": "płakał", "is_correct": False},
            {"word": "płacze", "is_correct": False},
            {"word": "płakały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___________ (być) zadowoleni.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "są", "is_correct": True},
            {"word": "jest", "is_correct": False},
            {"word": "byli", "is_correct": False},
            {"word": "były", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___________ (piec) ciasto.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "pieczą", "is_correct": True},
            {"word": "piecze", "is_correct": False},
            {"word": "pieczemy", "is_correct": False},
            {"word": "piecą", "is_correct": False}
        ]
    },
    {
        "sentence": "Ona ___________ (piec) ciasto.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "piecze", "is_correct": True},
            {"word": "pieczą", "is_correct": False},
            {"word": "pieczemy", "is_correct": False},
            {"word": "piecą", "is_correct": False}
        ]
    }
]

# First delete all existing sentences
db.query(Sentence).delete()

# Add sentences and their options to the database
for sentence_data in sample_sentences:
    sentence = Sentence(
        sentence=sentence_data["sentence"],
        tense=sentence_data["tense"],
        difficulty_level=sentence_data["difficulty_level"]
    )
    db.add(sentence)
    db.flush()  # Get the id of the newly created sentence
    
    # Add word options
    for option_data in sentence_data["options"]:
        option = WordOption(
            unique_id=str(uuid.uuid4()),
            word=option_data["word"],
            is_correct=option_data["is_correct"],
            sentence_id=sentence.id
        )
        db.add(option)

# Commit the changes
db.commit()

print("Database initialized successfully with multiple choice options!")
db.close()
