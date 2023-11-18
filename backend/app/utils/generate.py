from boto3 import Session
import openai
import os

from dotenv import load_dotenv
load_dotenv()

session = Session(
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
polly = session.client("polly", region_name="us-east-1")

def generate_audio_stream(voice_id: str, text: str):
    # TODO Add exception handling to this
    response = polly.synthesize_speech(
        Engine='neural',
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice_id
    )
    if "AudioStream" in response:
        return response["AudioStream"]
    else:
        return None
