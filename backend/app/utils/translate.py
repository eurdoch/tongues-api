import json
from app.utils.models import get_chat_response

def translate(source_language: str, target_language, sentence: str):
    return get_chat_response(f"Translate '{sentence}' from {source_language} to {target_language}. ONLY return the translation")

def translate_word(source_language: str, target_language: str, word: str):
	return get_chat_response(f"Return the different translations of the {source_language} word {word} to {target_language}.  ONLY return the translations as a comma separated list.")
