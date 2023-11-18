import json
from app.utils.models import get_chat_response

def translate(source_language: str, target_language, sentence: str):
    return get_chat_response(f"Translate '{sentence}' from {source_language} to {target_language}. ONLY return the translation")

def translate_word(source_language: str, target_language: str, word: str):
    response = get_chat_response(f"Generate the different translations of the {source_language} word '{word}' in {target_language} as a JSON object of the form {{translations: ... }}. ONLY return the JSON object.")
    response = json.loads(response.replace('\n', ''))
    return response['translations']
