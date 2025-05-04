<<<<<<< HEAD
# polish-grammar-api
# Polish Grammar Learning Backend

This is a FastAPI backend for a Polish grammar learning application. The backend provides endpoints for fetching sentences with missing verbs and verifying user answers.

## Features

- Store thousands of Polish sentences with missing verbs
- Random sentence retrieval
- Answer verification
- Difficulty levels
- Verb conjugation forms and tenses

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /api/sentences/random` - Get a random sentence for practice
- `POST /api/sentences/verify` - Verify user's answer
- `POST /api/sentences` - Add new sentences to the database

## Database

The application uses SQLite by default, but can be configured to use PostgreSQL by modifying the `SQLALCHEMY_DATABASE_URL` in `main.py`.

## Example Usage

```python
# Get a random sentence
response = requests.get("http://localhost:8000/api/sentences/random")
sentence = response.json()

# Verify user's answer
response = requests.post(
    "http://localhost:8000/api/sentences/verify",
    json={
        "sentence_id": sentence["id"],
        "user_answer": "user's answer here"
    }
)
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
