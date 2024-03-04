from app.utils.models import get_chat_response

# TODO generate response for all languages
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
    difficulty: str = "beginner",
):
    response = get_chat_response(prompt=f"Generate a short response to continue the following conversation in {language}. ONLY return the response.\n{history}Human: {text}\nAI:")
    if history is None:
        newHistory = f"Human: {text}\nAI:{response}"
    else:
        historyList = history.split("\n")
        historyList.append(f"Human: {text}")
        historyList.append(f"AI:{response}")
        newHistory = ""
        newHistory = "".join(f"{s}\n" for s in historyList[-20:])
        newHistory = newHistory[:-1]
    return {
        "is_valid": True,
        "grammar_correct": True, # This is always true for now as does nott work well
        "history": newHistory,
        "response": response
    }
