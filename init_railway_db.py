import sqlite3
import os
import json
import uuid
from datetime import datetime
import bcrypt

# Ensure the database file exists
db_path = "./database.db"
print(f"Initializing database at {os.path.abspath(db_path)}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables directly with SQLite
print("Creating tables...")

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
)
""")

# Create themes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    parent_theme_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_theme_id) REFERENCES themes (id)
)
""")

# Create sentences table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence TEXT NOT NULL,
    tense TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL,
    theme_id INTEGER NOT NULL,
    order_in_theme INTEGER NOT NULL,
    FOREIGN KEY (theme_id) REFERENCES themes (id)
)
""")

# Create word_options table
cursor.execute("""
CREATE TABLE IF NOT EXISTS word_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_id TEXT NOT NULL,
    word TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    sentence_id INTEGER NOT NULL,
    FOREIGN KEY (sentence_id) REFERENCES sentences (id)
)
""")

# Create user_progress table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    theme_id INTEGER NOT NULL,
    current_sentence_index INTEGER NOT NULL DEFAULT 0,
    completed_sentences INTEGER NOT NULL DEFAULT 0,
    last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (theme_id) REFERENCES themes (id)
)
""")

conn.commit()
print("Tables created successfully")

# Check if test user exists, create if not
cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("test1@mail.ru",))
user_count = cursor.fetchone()[0]

if user_count == 0:
    print("Creating test user...")
    # Hash the password
    password = "Qwerty12"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    # Insert the user
    cursor.execute(
        "INSERT INTO users (email, hashed_password, created_at) VALUES (?, ?, ?)",
        ("test1@mail.ru", hashed_password, datetime.utcnow().isoformat())
    )
    conn.commit()
    print("Test user created successfully")
else:
    print(f"Test user already exists")

# Function to get or create a theme
def get_or_create_theme(theme_name, subtheme_name=None):
    if subtheme_name:
        # Check if parent theme exists
        cursor.execute("SELECT id FROM themes WHERE name = ? AND parent_theme_id IS NULL", (theme_name,))
        parent_result = cursor.fetchone()
        
        if parent_result:
            parent_id = parent_result[0]
        else:
            # Create parent theme
            cursor.execute(
                "INSERT INTO themes (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (theme_name, None, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
            )
            parent_id = cursor.lastrowid
            conn.commit()
        
        # Check if subtheme exists
        cursor.execute("SELECT id FROM themes WHERE name = ? AND parent_theme_id = ?", (subtheme_name, parent_id))
        subtheme_result = cursor.fetchone()
        
        if subtheme_result:
            return subtheme_result[0]
        else:
            # Create subtheme
            cursor.execute(
                "INSERT INTO themes (name, description, parent_theme_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (subtheme_name, None, parent_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
            )
            theme_id = cursor.lastrowid
            conn.commit()
            return theme_id
    else:
        # Check if theme exists
        cursor.execute("SELECT id FROM themes WHERE name = ? AND parent_theme_id IS NULL", (theme_name,))
        theme_result = cursor.fetchone()
        
        if theme_result:
            return theme_result[0]
        else:
            # Create theme
            cursor.execute(
                "INSERT INTO themes (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (theme_name, None, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
            )
            theme_id = cursor.lastrowid
            conn.commit()
            return theme_id

# Import sentences from JSON file
def import_sentences():
    json_path = "sentences_data.json"
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found, skipping sentence import")
        return
    
    print(f"Importing sentences from {json_path}...")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check if sentences already exist
        cursor.execute("SELECT COUNT(*) FROM sentences")
        sentence_count = cursor.fetchone()[0]
        
        if sentence_count > 0:
            print(f"Found {sentence_count} existing sentences, skipping import")
            return
        
        for theme_entry in data:
            theme_name = theme_entry["theme"]
            subtheme_name = theme_entry.get("subtheme")
            theme_id = get_or_create_theme(theme_name, subtheme_name)
            
            for idx, sent in enumerate(theme_entry["sentences"]):
                # Insert sentence
                cursor.execute(
                    "INSERT INTO sentences (sentence, tense, difficulty_level, theme_id, order_in_theme) VALUES (?, ?, ?, ?, ?)",
                    (sent["sentence"], sent["tense"], sent["difficulty_level"], theme_id, idx)
                )
                sentence_id = cursor.lastrowid
                
                # Insert word options
                for option in sent["word_options"]:
                    cursor.execute(
                        "INSERT INTO word_options (unique_id, word, is_correct, sentence_id) VALUES (?, ?, ?, ?)",
                        (str(uuid.uuid4()), option["word"], option["is_correct"], sentence_id)
                    )
        
        conn.commit()
        print("Sentences imported successfully!")
    except Exception as e:
        print(f"Error importing sentences: {str(e)}")

# Import sentences
import_sentences()

# Close the connection
conn.close()
print("Database initialization complete")
