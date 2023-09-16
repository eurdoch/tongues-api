from contextlib import closing
from io import BytesIO
import openai
import os
from boto3 import Session
 
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Body,
    Path,
    Depends,
)

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from app.models.translate import (
    TranslationRequest, 
    TranslationResponse, 
    WordInfo,
    WordShortView,
    Word,
)
from app.app import app
from app.utils.auth import is_authorized
from app.utils.translate import generate_explanation
from app.utils.generate import generate_audio_stream

session = Session(
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
translator = session.client("translate", region_name="us-east-1")

ISO_TO_AWS_LANG = {
    'es-US': 'es',
    'en-US': 'en',
    'nl-NL': 'nl',
    'fr-FR': 'fr',
    'de-DE': 'de',
    'it-IT': 'it',
    'is-IS': 'is',
    'pt-PT': 'pt-PT',
    'pt-BR': 'pt',
    'ru-RU': 'ru',
    'ja-JP': 'jp',
    'arb': 'ar',
    'sv-SE': 'sv',
}

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

def parse_word_senses_completion(message: str):
    inds = []
    senses = []
    for (i, c) in enumerate(message):
        if c.isnumeric():
            inds.append(i)        
    for (i, spliti) in enumerate(inds):
        substring = ""
        if i != 0:
            substring = message[inds[i-1]:inds[i]]
            if ':' in substring:
                sense, explanation = substring.split(':')
                sense = sense.split('.')[1].split('(')[0].strip()
                explanation = explanation.strip()
                senses.append({'sense': sense, 'explanation': explanation})
    return senses

@router.post(
    "/translate"
)
async def translate_text(
    translationRequest: TranslationRequest,
):
    system_template = """You are an translator that translates 
    {source_language} to {target_language}. The user will pass in text and 
    you will translate the text.
    ONLY return the translation in {target_language}.
    """ 
    system_prompt_message = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{text}"
    human_prompt_message = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatMessagePromptTemplate([system_prompt_message, human_prompt_message])
    chain = LLMChain(
        # TODO Refactor the llm to a separate file that can be accessed by all endpoints
        llm=ChatOpenAI(),
        prompt=chat_prompt,
    )
    response = chain.run(
        text=translationRequest.sentence, 
        source_language=translationRequest.sourceLang,
        target_language=translationRequest.targetLang,
    )
    return {
        "translation": response
    }

ISO_TO_LANG = {
    'en_US': 'American English',
    'es_US': 'Spanish',
    'nl_NL': 'Dutch',
    'de_DE': 'German',
    'fr_FR': 'French',
    'it_IT': 'Italian',
    'is_IS': 'Icelandic',
    'pt_PT': 'Portuguese (European)',
    'pt_BR': 'Portuguese (Brazilian)',
    'ru_RU': 'Russian',
    'ja_JP': 'Japanese',
    'arb': 'Arabic',
    'sv_SE': 'Swedish',
}

ISO_TO_VOICE_ID = {
    'en_US': 'Joey',
    'nl_NL': 'Ruben',
    'es_US': 'Lupe',
    'de_DE': 'Hans',
    'fr_FR': 'Mathieu',
    'it_IT': 'Giorgio',
    'is_IS': 'Karl',
    'pt_PT': 'Cristiano',
    'pt_BR': 'Ricardo',
    'ru_RU': 'Maxim',
    'ja_JP': 'Takumi',
    'arb': 'Zeina',
    'sv_SE': 'Astrid',
}

@router.post(
    "/word"
)
async def explain_word(
    wordInfo: WordInfo,
):
    parsedNativeLang = wordInfo.nativeLang.replace('-', '_')
    parsedStudyLang = wordInfo.studyLang.replace('-', '_')
    db_word = await Word.find_one(
       Word.word == wordInfo.word,
       Word.language == parsedStudyLang,
    )
    if db_word is None or db_word.explanation.__dict__[parsedNativeLang] == "":
        completion = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {
                    "role": "user", 
                    "content": "Explain the " + ISO_TO_LANG[parsedStudyLang] + " word " 
                        + "'" + wordInfo.word + "' as it used in the " + ISO_TO_LANG[parsedStudyLang]
                        + " language, with the explanation written in the " + ISO_TO_LANG[parsedNativeLang]
                        + " language. Include the various translations of the word in the "
                        + ISO_TO_LANG[parsedNativeLang] + " language."
                }
            ]
        ) 
        if db_word is None:
            explanation = generate_explanation(
                explanation=completion.choices[0].message.content,
                language=parsedNativeLang,
            )
            # generate audio of word
            stream = generate_audio_stream(
                voice_id=ISO_TO_VOICE_ID[parsedStudyLang],
                text=wordInfo.word,
            )
            f = BytesIO()
            with closing(stream) as stream:
                try:
                    f.write(stream.read())
                except IOError as error:
                    print(error)
            f.seek(0)
            content = f.read()
            audio_id = await app.audio_bucket.upload_from_stream("test_file", content, metadata={"contentType": "audio/mp3"})
            new_word = Word(
                word=wordInfo.word,
                language=parsedStudyLang,
                explanation=explanation,
                audio_id=audio_id,
            )
            await new_word.save()
            return_word = await Word.find_one(Word.word == new_word.word)
            return_word = return_word.__dict__
            return_word['explanation'] = getattr(return_word['explanation'], parsedNativeLang)
            return_word['audio_id'] = str(return_word['audio_id'])
            return return_word
        else:
            db_word.explanation.__setattr__(parsedNativeLang, completion.choices[0].message.content)
            await db_word.save()
            return_word = await Word.find_one(Word.word == db_word.word)
            return_word = return_word.__dict__
            return_word['explanation'] = getattr(return_word['explanation'], parsedNativeLang)
            return_word['audio_id'] = str(return_word['audio_id'])
            return return_word
    else:
        return_word = await Word.find_one(Word.word == db_word.word)
        return_word = return_word.__dict__
        return_word['explanation'] = getattr(return_word['explanation'], parsedNativeLang)
        return_word['audio_id'] = str(return_word['audio_id'])
        return return_word
