#CONNECTION TO THE MAIN CODE
import random
import requests
import json
from typing import List, Dict
from difflib import get_close_matches
import spacy

nlp = spacy.load('en_core_web_md')

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: List[str]) -> str:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str:
    for q in knowledge_base["questions"]:
        if q["question"].lower() == question.lower():
            return q["answer"]
    return "I don't know the answer. Can you teach me?"

def get_country_information(country: str) -> str:
    url = f'https://restcountries.com/v3.1/name/{country}'
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data:
            country_info = data[0]
            return (
                f"{country_info['name']['common']} is a country in {country_info['region']}. "
                f"The capital city is {country_info.get('capital', ['unknown'])[0]}. "
                f"It has a population of {country_info.get('population', 'unknown')}. "
                f"The official languages are {', '.join(country_info['languages'].values())}. "
                f"The currency is {', '.join([currency['name'] for currency in country_info['currencies'].values()])}."
            )
        else:
            return "Sorry, I couldn't fetch information about that country."
    except requests.exceptions.RequestException as e:
        return f"Error fetching country information: {str(e)}"
    except (KeyError, IndexError):
        return "Error: Unexpected response format from API"

def detect_activity_intent(user_input: str) -> bool:
    keywords = ["activities", "things to do", "what can I do"]
    for keyword in keywords:
        if keyword in user_input.lower():
            return True
    return False

def chat_bot():
    knowledge_base = load_knowledge_base('knowledge_base.json')

    print("Welcome to the Travel Bot!")
    while True:
        user_input = input('You: ')

        if user_input.lower() == 'quit':
            break

        
        user_doc = nlp(user_input)
        country_entities = [ent.text for ent in user_doc.ents if ent.label_ == "GPE"]

        if country_entities:
            country = country_entities[0]
            country_info = get_country_information(country)
            print(f'Bot: {country_info}')
        elif detect_activity_intent(user_input):
            print('Bot: Here are some activities you can do:')
            
        else:
            best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                print(f'Bot: {answer}')
            else:
                print('Bot: I don\'t know the answer. Can you teach me?')
                new_answer = input('Type the answer or "skip" to skip: ')

                if new_answer.lower() != 'skip':
                    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    print('Bot: Thank you! I learnt a new response!')

    
    save_knowledge_base('knowledge_base.json', knowledge_base)

if '__name__' == '__main__':
    chat_bot()