from app.models.translate import Explanation

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

def generate_explanation(explanation: str, language: str):
    expl_dict = {}
    for field in Explanation.__fields__:
        expl_dict[field] = explanation if field == language else ""
    return Explanation.parse_obj(expl_dict)

def translate(source_language: str, target_language, sentence: str):
    system_template = """You are an translator that translates 
    {source_language} to {target_language}. The user will pass in text and 
    you will translate the text.
    ONLY return the translation in {target_language}.
    """ 
    system_prompt_message = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{text}"
    human_prompt_message = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt_message, human_prompt_message])
    chain = LLMChain(
        # TODO Refactor the llm to a separate file that can be accessed by all endpoints
        llm=ChatOpenAI(),
        prompt=chat_prompt,
    )
    return chain.run(
        text=sentence, 
        source_language=source_language,
        target_language=target_language,
    )