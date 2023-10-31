from app.utils.models import get_chat_response

MISUNDERSTOOD_RESPONSE = {
    "Dutch": "Het spijt me, ik begreep je niet.",
    "English": "Sorry, I didn't understand you.",
    "French": "Je suis désolé, je ne t'ai pas compris.",
    "Spanish (American)": "Lo siento, no te entendí.",
    "Italian": "Mi dispiace, non ti ho capito.",
    "German": "Es tut mir leid, ich habe dich nicht verstanden."
}

def get_chat_response_by_language(
    text: str,
    language: str,
    history: str = None,
):
    response = get_chat_response(f"Generate a sentence to continue the following conversation in {language}. ONLY return the sentence.\n{history}Human: {text}\nAI:")
    newHistory = f"Human:{text}\nAI:{response}" if history is None else history + f"\nHuman:{text}\nAI:{response}"
    print(newHistory)
    return {
        "is_valid": True,
        "grammar_correct": True,
        "history": newHistory,
        "response": response
    }
