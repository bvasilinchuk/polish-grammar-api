import requests
import json

# Get a random sentence
response = requests.get('http://localhost:8000/api/sentences/random')
if response.status_code == 200:
    sentence = response.json()
    print("\nRandom Sentence:")
    print(json.dumps(sentence, indent=2))
else:
    print(f"Error: {response.status_code}")

# Example of verifying an answer
# Note: You'll need to use the actual sentence_id from the random sentence
sentence_id = sentence['id']
user_answer = "your_answer_here"  # Replace with your actual answer

verify_response = requests.post(
    'http://localhost:8000/api/sentences/verify',
    json={
        "sentence_id": sentence_id,
        "user_answer": user_answer
    }
)

if verify_response.status_code == 200:
    result = verify_response.json()
    print("\nVerification Result:")
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {verify_response.status_code}")
