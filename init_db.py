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
        "sentence": "Jeremi ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "zjadł", "is_correct": False},
            {"word": "odpowiedział", "is_correct": True},
            {"word": "widział", "is_correct": False},
            {"word": "przyszedł", "is_correct": False}
        ]
    },
    {
        "sentence": "Jędrzej ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "zrobił", "is_correct": True},
            {"word": "przyszedł", "is_correct": False},
            {"word": "obejrzał", "is_correct": False},
            {"word": "poszedł", "is_correct": False}
        ]
    },
    {
        "sentence": "Leon ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "powiedział", "is_correct": True},
            {"word": "zrozumiał", "is_correct": False},
            {"word": "przyszedł", "is_correct": False},
            {"word": "obejrzał", "is_correct": False}
        ]
    },
    {
        "sentence": "Maks ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "dostał", "is_correct": False},
            {"word": "widział", "is_correct": True},
            {"word": "czytał", "is_correct": False},
            {"word": "napisał", "is_correct": False}
        ]
    },
    {
        "sentence": "Hubert ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "kupił", "is_correct": False},
            {"word": "obejrzał", "is_correct": False},
            {"word": "poszedł", "is_correct": False},
            {"word": "czytał", "is_correct": True}
        ]
    },
    {
        "sentence": "Stefan ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "powiedział", "is_correct": False},
            {"word": "obejrzał", "is_correct": False},
            {"word": "wypił", "is_correct": False},
            {"word": "przyszedł", "is_correct": True}
        ]
    },
    {
        "sentence": "Marcin ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "napisał", "is_correct": False},
            {"word": "obejrzał", "is_correct": True},
            {"word": "poszedł", "is_correct": False},
            {"word": "zjadł", "is_correct": False}
        ]
    },
    {
        "sentence": "Ryszard ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "powiedział", "is_correct": False},
            {"word": "czytał", "is_correct": True},
            {"word": "incorrect", "is_correct": False},
            {"word": "dostał", "is_correct": False}
        ]
    },
    {
        "sentence": "Dariusz ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "zjadł", "is_correct": True},
            {"word": "odpowiedział", "is_correct": False},
            {"word": "zrozumiał", "is_correct": False},
            {"word": "obejrzał", "is_correct": False}
        ]
    },
    {
        "sentence": "Oskar ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "poszedł", "is_correct": False},
            {"word": "zjadł", "is_correct": True},
            {"word": "sprzedał", "is_correct": False},
            {"word": "zrobił", "is_correct": False}
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
