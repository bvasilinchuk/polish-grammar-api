import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Sentence, WordOption, Theme

# Adjust the DB path if needed
db_url = "sqlite:///./database.db"
engine = create_engine(db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_or_create_theme(db, theme_name, subtheme_name=None):
    if subtheme_name:
        parent_theme = db.query(Theme).filter(Theme.name == theme_name, Theme.parent_theme_id == None).first()
        if not parent_theme:
            parent_theme = Theme(name=theme_name)
            db.add(parent_theme)
            db.commit()
            db.refresh(parent_theme)
        theme = db.query(Theme).filter(Theme.name == subtheme_name, Theme.parent_theme_id == parent_theme.id).first()
        if not theme:
            theme = Theme(name=subtheme_name, parent_theme_id=parent_theme.id)
            db.add(theme)
            db.commit()
            db.refresh(theme)
        return theme
    else:
        theme = db.query(Theme).filter(Theme.name == theme_name, Theme.parent_theme_id == None).first()
        if not theme:
            theme = Theme(name=theme_name)
            db.add(theme)
            db.commit()
            db.refresh(theme)
        return theme

def import_sentences(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    db = SessionLocal()
    try:
        for theme_entry in data:
            theme_name = theme_entry["theme"]
            subtheme_name = theme_entry.get("subtheme")
            theme = get_or_create_theme(db, theme_name, subtheme_name)
            for idx, sent in enumerate(theme_entry["sentences"]):
                # Check if the sentence already exists for this theme and order
                existing = db.query(Sentence).filter(
                    Sentence.sentence == sent["sentence"],
                    Sentence.theme_id == theme.id
                ).first()
                if existing:
                    continue
                sentence = Sentence(
                    sentence=sent["sentence"],
                    tense=sent["tense"],
                    difficulty_level=sent["difficulty_level"],
                    theme_id=theme.id,
                    order_in_theme=idx
                )
                db.add(sentence)
                db.flush()  # Get sentence.id
                for option in sent["word_options"]:
                    word_option = WordOption(
                        unique_id=str(uuid.uuid4()),
                        word=option["word"],
                        is_correct=option["is_correct"],
                        sentence_id=sentence.id
                    )
                    db.add(word_option)
        db.commit()
        print("Sentences imported successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    import_sentences("sentences_data.json")
