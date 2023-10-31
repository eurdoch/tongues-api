from app.utils.models import get_chat_response

def translate(source_language: str, target_language, sentence: str):
    return get_chat_response(f"Translate {sentence} from {source_language} to {target_language}. ONLY return the translation")
