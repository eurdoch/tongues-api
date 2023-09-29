from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.chains import (
    ConversationChain,
    LLMChain,
)
from langchain.chat_models import ChatOpenAI
from app.app import llm

llmzerotemp = ChatOpenAI(temperature=0.0)
llm4 = ChatOpenAI(model="gpt-4")

MISUNDERSTOOD_RESPONSE = {
    "Dutch": "Het spijt me, ik begreep je niet.",
    "English": "Sorry, I didn't understand you.",
    "French": "Je suis désolé, je ne t'ai pas compris.",
    "Spanish": "Lo siento, no te entendí.",
    "Italian": "Mi dispiace, non ti ho capito.",
    "German": "Es tut mir leid, ich habe dich nicht verstanden."
}

def build_memory(history: str) -> ConversationBufferMemory:
    memory = ConversationBufferMemory()
    if history is not None:
        messages = history.split('\n')
        messages = messages[:10] if len(messages) > 10 else messages
        for message in messages:
            speaker, text = message.split(':')
            if speaker == "Human":
                memory.chat_memory.add_user_message(text[1:])
            elif speaker == "AI":
                memory.chat_memory.add_ai_message(text[1:])
    return memory

def is_valid_text(
    text: str,
    language: str,
):
    template = """Does the text "{text}" contain words from the {language} language?
    ONLY return Yes or No"""
    prompt = PromptTemplate.from_template(template) 
    chain = LLMChain(
        llm=llmzerotemp,
        prompt=prompt,
    )
    return chain.run({
        "text": text,
        "language": language
    })

def is_valid_grammar(
    text: str,
    language: str,
):
    template = """Is the text {text} gramatically correct in the {language} language?  ONLY respond with yes or no"""
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(
        llm=llmzerotemp,
        prompt=prompt,
    )
    return chain.run({
        "language": language,
        "text": text,
    })

def get_grammar_explanation(
    text: str,
    language: str
):
    template = """Explain why the text {text} is gramatically incorrect in {language} language."""
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(
        llm=llm,
        prompt=prompt
    )
    return chain.run({
        "language": language,
        "text": text
    })

def get_chat_response_by_language(
    text: str,
    language: str,
    history: str = None,
    system_message: str = """You are {language} person having a friendly conversation in {language}.
    ONLY respond as if you are a real person having a conversation.
    """
):
    return_value = {}
    if is_valid_text(text=text, language=language).replace(".", "") == "No":
        if is_valid_grammar(text=text, language=language).replace(".", "") == "No":
            memory = build_memory(history=history)
            template = system_message + """

            Current conversation:
            {history}
            Human: {input}
            AI:"""
            prompt_template = PromptTemplate(
                input_variables=["history", "input", "language"], 
                template=template
            )

            conversation_chain = ConversationChain(
                llm=llm,
                prompt=prompt_template.partial(language=language),
                memory=memory
            )
            response = conversation_chain.predict(input=text)
            history = conversation_chain.memory.buffer_as_str

            return_value = {
                "is_valid": True,
                "grammar_correct": True,
                "history": history,
                "response": response
            }
        else:
            return_value = {
                "is_valid": True,
                "grammar_correct": False,
                "history": history,
                "response": get_grammar_explanation(text=text, language=language),
            }
    else:
        return_value = {
            "is_valid": False,
            "grammar_correct": True,
            "history": history,
            "response": MISUNDERSTOOD_RESPONSE[language],
        }
    return return_value

# TODO This is not being used, phase out
def get_suggestions_by_language(
    history: str,
    language: str,
    system_message: str,
):
    memory = build_memory(history)
    template = system_message + """

    Current conversation:
    {history}
    AI:"""
    prompt_template = PromptTemplate(
        input_variables=["history", "language"], 
        template=template
    )
    conversation_chain = ConversationChain(
        llm=llm,
        prompt=prompt_template.partial(language=language),
        verbose=True,
        memory=memory
    )

    suggestions = []
    for _ in range(0,3):
        suggestions.append(conversation_chain.predict())

    return {
        "suggestions": suggestions
    }
    

