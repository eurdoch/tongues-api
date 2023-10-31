import os
import json

from dotenv import load_dotenv
load_dotenv()

from boto3 import Session
session = Session(
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)
bedrock = session.client('bedrock-runtime')

def get_chat_response(prompt):
    body = json.dumps({
        "prompt": "Human:" + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": 300,
        "temperature": 1.0,
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
