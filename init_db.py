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
    # Present tense - regular verbs
    {
        "sentence": "Anna ___ do szkoły.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "idzie", "is_correct": True},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ do domu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "idą", "is_correct": True},
            {"word": "idzie", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    {
        "sentence": "My ___ do pracy.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "idziemy", "is_correct": True},
            {"word": "idzie", "is_correct": False},
            {"word": "idą", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    # Past tense - regular verbs
    {
        "sentence": "Anna ___ do szkoły.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "szła", "is_correct": True},
            {"word": "szli", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ do domu.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "szli", "is_correct": True},
            {"word": "szła", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    # Present tense - irregular verbs
    {
        "sentence": "On ___ do domu.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idzie", "is_correct": True},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    {
        "sentence": "Ona ___ do pracy.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idzie", "is_correct": True},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    # Past tense - irregular verbs
    {
        "sentence": "On ___ do domu.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szedł", "is_correct": True},
            {"word": "szła", "is_correct": False},
            {"word": "szli", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    {
        "sentence": "Ona ___ do pracy.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szła", "is_correct": True},
            {"word": "szedł", "is_correct": False},
            {"word": "szli", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ obiad.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "je", "is_correct": True},
            {"word": "jemy", "is_correct": False},
            {"word": "jedzą", "is_correct": False},
            {"word": "jedź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ kolację.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "jedzą", "is_correct": True},
            {"word": "je", "is_correct": False},
            {"word": "jemy", "is_correct": False},
            {"word": "jedź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ obiad.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "zjadła", "is_correct": True},
            {"word": "zjadł", "is_correct": False},
            {"word": "zjadli", "is_correct": False},
            {"word": "zjadły", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ kolację.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "zjadli", "is_correct": True},
            {"word": "zjadła", "is_correct": False},
            {"word": "zjadł", "is_correct": False},
            {"word": "zjadły", "is_correct": False}
        ]
    },
    # Present tense - być (to be)
    {
        "sentence": "Anna ___ w domu.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "jest", "is_correct": True},
            {"word": "są", "is_correct": False},
            {"word": "jestem", "is_correct": False},
            {"word": "bądź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ w szkole.",
        "tense": "present",
        "difficulty_level": 1,
        "options": [
            {"word": "są", "is_correct": True},
            {"word": "jest", "is_correct": False},
            {"word": "jestem", "is_correct": False},
            {"word": "bądź", "is_correct": False}
        ]
    },
    # Past tense - być (to be)
    {
        "sentence": "Anna ___ w domu.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "była", "is_correct": True},
            {"word": "był", "is_correct": False},
            {"word": "byli", "is_correct": False},
            {"word": "były", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ w szkole.",
        "tense": "past",
        "difficulty_level": 2,
        "options": [
            {"word": "byli", "is_correct": True},
            {"word": "była", "is_correct": False},
            {"word": "był", "is_correct": False},
            {"word": "były", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ książkę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "czyta", "is_correct": True},
            {"word": "czytają", "is_correct": False},
            {"word": "czytamy", "is_correct": False},
            {"word": "czytaj", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ gazetę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "czytają", "is_correct": True},
            {"word": "czyta", "is_correct": False},
            {"word": "czytamy", "is_correct": False},
            {"word": "czytaj", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ książkę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "czytała", "is_correct": True},
            {"word": "czytał", "is_correct": False},
            {"word": "czytali", "is_correct": False},
            {"word": "czytały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ gazetę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "czytali", "is_correct": True},
            {"word": "czytała", "is_correct": False},
            {"word": "czytał", "is_correct": False},
            {"word": "czytały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ do sklepu.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idzie", "is_correct": True},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ do parku.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idą", "is_correct": True},
            {"word": "idzie", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ do sklepu.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szła", "is_correct": True},
            {"word": "szli", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ do parku.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szli", "is_correct": True},
            {"word": "szła", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ kawę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "pije", "is_correct": True},
            {"word": "piją", "is_correct": False},
            {"word": "pijemy", "is_correct": False},
            {"word": "pij", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ herbatę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "piją", "is_correct": True},
            {"word": "pije", "is_correct": False},
            {"word": "pijemy", "is_correct": False},
            {"word": "pij", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ kawę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "piła", "is_correct": True},
            {"word": "pił", "is_correct": False},
            {"word": "piili", "is_correct": False},
            {"word": "piły", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ herbatę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "piili", "is_correct": True},
            {"word": "piła", "is_correct": False},
            {"word": "pił", "is_correct": False},
            {"word": "piły", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ film.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "ogląda", "is_correct": True},
            {"word": "oglądają", "is_correct": False},
            {"word": "oglądamy", "is_correct": False},
            {"word": "oglądaj", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ serial.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "oglądają", "is_correct": True},
            {"word": "ogląda", "is_correct": False},
            {"word": "oglądamy", "is_correct": False},
            {"word": "oglądaj", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ film.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "oglądała", "is_correct": True},
            {"word": "oglądał", "is_correct": False},
            {"word": "oglądali", "is_correct": False},
            {"word": "oglądały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ serial.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "oglądali", "is_correct": True},
            {"word": "oglądała", "is_correct": False},
            {"word": "oglądał", "is_correct": False},
            {"word": "oglądały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na spacer.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "wychodzi", "is_correct": True},
            {"word": "wychodzą", "is_correct": False},
            {"word": "wychodzimy", "is_correct": False},
            {"word": "wyjdź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na plażę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "wychodzą", "is_correct": True},
            {"word": "wychodzi", "is_correct": False},
            {"word": "wychodzimy", "is_correct": False},
            {"word": "wyjdź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na spacer.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "wyjechała", "is_correct": True},
            {"word": "wyjechał", "is_correct": False},
            {"word": "wyjechali", "is_correct": False},
            {"word": "wyjechały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na plażę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "wyjechali", "is_correct": True},
            {"word": "wyjechała", "is_correct": False},
            {"word": "wyjechał", "is_correct": False},
            {"word": "wyjechały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na lotnisko.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "leci", "is_correct": True},
            {"word": "lecą", "is_correct": False},
            {"word": "leczemy", "is_correct": False},
            {"word": "lecź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na wakacje.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "lecą", "is_correct": True},
            {"word": "leci", "is_correct": False},
            {"word": "leczemy", "is_correct": False},
            {"word": "lecź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na lotnisko.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "leciała", "is_correct": True},
            {"word": "leciał", "is_correct": False},
            {"word": "lecieli", "is_correct": False},
            {"word": "leciały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na wakacje.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "lecieli", "is_correct": True},
            {"word": "leciała", "is_correct": False},
            {"word": "leciał", "is_correct": False},
            {"word": "leciały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na koncert.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idzie", "is_correct": True},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na festiwal.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idą", "is_correct": True},
            {"word": "idzie", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na koncert.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szła", "is_correct": True},
            {"word": "szli", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na festiwal.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szli", "is_correct": True},
            {"word": "szła", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na spacer.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "wychodzi", "is_correct": True},
            {"word": "wychodzą", "is_correct": False},
            {"word": "wychodzimy", "is_correct": False},
            {"word": "wyjdź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na plażę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "wychodzą", "is_correct": True},
            {"word": "wychodzi", "is_correct": False},
            {"word": "wychodzimy", "is_correct": False},
            {"word": "wyjdź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na spacer.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "wyjechała", "is_correct": True},
            {"word": "wyjechał", "is_correct": False},
            {"word": "wyjechali", "is_correct": False},
            {"word": "wyjechały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na plażę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "wyjechali", "is_correct": True},
            {"word": "wyjechała", "is_correct": False},
            {"word": "wyjechał", "is_correct": False},
            {"word": "wyjechały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na lotnisko.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "leci", "is_correct": True},
            {"word": "lecą", "is_correct": False},
            {"word": "leczemy", "is_correct": False},
            {"word": "lecź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na wakacje.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "lecą", "is_correct": True},
            {"word": "leci", "is_correct": False},
            {"word": "leczemy", "is_correct": False},
            {"word": "lecź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na lotnisko.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "leciała", "is_correct": True},
            {"word": "leciał", "is_correct": False},
            {"word": "lecieli", "is_correct": False},
            {"word": "leciały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na wakacje.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "lecieli", "is_correct": True},
            {"word": "leciała", "is_correct": False},
            {"word": "leciał", "is_correct": False},
            {"word": "leciały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na koncert.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idzie", "is_correct": True},
            {"word": "idą", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na festiwal.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "idą", "is_correct": True},
            {"word": "idzie", "is_correct": False},
            {"word": "idziemy", "is_correct": False},
            {"word": "idź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na koncert.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szła", "is_correct": True},
            {"word": "szli", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na festiwal.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "szli", "is_correct": True},
            {"word": "szła", "is_correct": False},
            {"word": "szedł", "is_correct": False},
            {"word": "szły", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na spacer.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "wychodzi", "is_correct": True},
            {"word": "wychodzą", "is_correct": False},
            {"word": "wychodzimy", "is_correct": False},
            {"word": "wyjdź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na plażę.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "wychodzą", "is_correct": True},
            {"word": "wychodzi", "is_correct": False},
            {"word": "wychodzimy", "is_correct": False},
            {"word": "wyjdź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na spacer.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "wyjechała", "is_correct": True},
            {"word": "wyjechał", "is_correct": False},
            {"word": "wyjechali", "is_correct": False},
            {"word": "wyjechały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na plażę.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "wyjechali", "is_correct": True},
            {"word": "wyjechała", "is_correct": False},
            {"word": "wyjechał", "is_correct": False},
            {"word": "wyjechały", "is_correct": False}
        ]
    },
    # Present tense - various verbs
    {
        "sentence": "Anna ___ na lotnisko.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "leci", "is_correct": True},
            {"word": "lecą", "is_correct": False},
            {"word": "leczemy", "is_correct": False},
            {"word": "lecź", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na wakacje.",
        "tense": "present",
        "difficulty_level": 2,
        "options": [
            {"word": "lecą", "is_correct": True},
            {"word": "leci", "is_correct": False},
            {"word": "leczemy", "is_correct": False},
            {"word": "lecź", "is_correct": False}
        ]
    },
    # Past tense - various verbs
    {
        "sentence": "Anna ___ na lotnisko.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "leciała", "is_correct": True},
            {"word": "leciał", "is_correct": False},
            {"word": "lecieli", "is_correct": False},
            {"word": "leciały", "is_correct": False}
        ]
    },
    {
        "sentence": "Oni ___ na wakacje.",
        "tense": "past",
        "difficulty_level": 3,
        "options": [
            {"word": "lecieli", "is_correct": True},
            {"word": "leciała", "is_correct": False},
            {"word": "leciał", "is_correct": False},
            {"word": "leciały", "is_correct": False}
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
