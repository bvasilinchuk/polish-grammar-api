import sqlite3
import os
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
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
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
    last_accessed TIMESTAMP NOT NULL,
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

# Close the connection
conn.close()
print("Database initialization complete")
