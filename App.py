
#connection to the index page
from flask import Flask, request, jsonify, render_template
import spacy
import nltk
from difflib import get_close_matches
from typing import List, Dict
import json

nlp = spacy.load('en_core_web_sm')
nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = nltk.WordNetLemmatizer()

with open('knowledge_base.json', 'r') as file:
    qa_pairs = json.load(file)["questions"]

app = Flask(__name__)

def preprocess_text(text: str) -> List[str]:
    doc = nlp(text.lower())
    tokens = [lemmatizer.lemmatize(token.text) for token in doc if not token.is_stop and token.is_alpha]
    return tokens

def get_best_match(question: str, qa_pairs: List[Dict[str, str]]) -> str:
    question_tokens = preprocess_text(question)
    questions = [qa["question"] for qa in qa_pairs]
    best_match = get_close_matches(' '.join(question_tokens), questions, n=1, cutoff=0.5)
    if best_match:
        for qa in qa_pairs:
            if qa["question"] == best_match[0]:
                return qa["answer"]
    return "I'm sorry, I don't have an answer for that."

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("user_input")
    response = get_best_match(user_input, qa_pairs)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
