from boto3 import Session
import json
import os

from dotenv import load_dotenv
load_dotenv()

session = Session(
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)
bedrock = session.client('bedrock-runtime')

MISUNDERSTOOD_RESPONSE = {
    "Dutch": "Het spijt me, ik begreep je niet.",
    "English": "Sorry, I didn't understand you.",
    "French": "Je suis désolé, je ne t'ai pas compris.",
    "Spanish (American)": "Lo siento, no te entendí.",
    "Italian": "Mi dispiace, non ti ho capito.",
    "German": "Es tut mir leid, ich habe dich nicht verstanden."
}

def get_chat_response(prompt):
    body = json.dumps({
        "prompt": "Human:" + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": 300,
        "temperature": 0.8,
        "top_p": 0.9,
    })
    response = bedrock.invoke_model(
        body=body,
        modelId=os.getenv('CLAUDE_INSTANT_MODEL'),
        accept='application/json',
        contentType='application/json',
    )
    response_body = json.loads(response.get('body').read())
    return response_body.get('completion')

def get_chat_response_by_language(
    text: str,
    language: str,
    history: str = None,
):
    return {
        "is_valid": True,
        "grammar_correct": True,
        "history": history,
        "response": get_chat_response(f"Generate a sentence to continue the following conversation in {language}. ONLY return the sentence.\n{history}Human: {text}\nAI:")
    }
