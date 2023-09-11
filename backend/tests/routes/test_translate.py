import pytest
from httpx import AsyncClient
from app.routes.translate import parse_word_senses_completion

def generate_invalid_token(token):
    return token[:-1] + "0" if token[-1] != "0" else "1"

# def test_parse_word_senses_completion():
#     message = '1. Soñar (verbo): La primera y más común acepción de \'dream\' en español es "soñar". Se refiere al acto de experimentar imágenes, pensamientos y sensaciones durante el sueño. Por ejemplo, "El niño soñaba con ser astronauta".\n\n2. Ilusionarse (verbo reflexivo): Otra acepción de \'dream\' en español es "ilusionarse". Se trata de tener grandes aspiraciones o deseos en la vida. Por ejemplo, "Ella sueña con viajar por todo el mundo".\n\n3. Fantasear (verbo): \'Dream\' también puede traducirse como "fantasear", que implica imaginar o crear situaciones irreales o ideales. Por ejemplo, "Durante la clase, él soñaba despierto con ser un famoso futbolista".\n\n4. Ambicionar (verbo): Esta acepción de \'dream\' se refiere a desear o anhelar intensamente alcanzar algo. Por ejemplo, "Él sueña con conseguir un trabajo mejor".\n\n5. Anhelar (verbo): \'Dream\' también puede significar "anhelar", que es desear intensamente algo. Por ejemplo, "Ella sueña con encontrar el amor verdadero".\n\n6. Idealizar (verbo): En algunos casos, \'dream\' se traduce como "idealizar", que implica crear una imagen idealizada de algo o alguien. Por ejemplo, "Ella sueña con una vida perfecta".\n\n7. Esperar (verbo): En ciertos contextos, \'dream\' se puede traducir como "esperar", que indica tener la esperanza de que algo suceda o se cumpla. Por ejemplo, "Sueño con que todos los niños del mundo tengan acceso a la educación".\n\nEstas son algunas de las diferentes acepciones del verbo \'dream\' en español. Cada una de ellas refleja diferentes aspectos del significado original en inglés.'
#     senses = parse_word_senses_completion(message)
#     assert senses == ['Soñar', 'Ilusionarse', 'Fantasear', 'Ambicionar', 'Anhelar', 'Esperar']

# TODO Mock Google Translate API, every call costs plata hombre
@pytest.mark.asyncio
async def test_successful_translation(client: AsyncClient, access_token: str):
    response = await client.post(
        "/api/v0/translate",
        json={
            "q": "I love you.",
            "target": "es",
        },
        headers={
            "Authorization": "Bearer " + access_token 
        }
    )
    assert response.status_code == 200
    translation = response.json()
    assert translation['translatedText'] == "Te amo."
    assert translation['detectedSourceLanguage'] == "en"

@pytest.mark.asyncio
async def test_unsuccessful_translate_invalid_auth(client: AsyncClient, access_token: str):
    invalid_token = generate_invalid_token(access_token)
    response = await client.post(
        "/api/v0/translate",
        json={
            "q": "",
            "target": "",
        },
        headers={
            "Authorization": "Bearer " + invalid_token
        }
    )
    assert response.status_code == 401

# @pytest.mark.asyncio
# async def test_translate_word_success(client: AsyncClient, access_token: str):
#     response = await client.post(
#         "/api/v0/translate/make",
#         json={
#             "targetLang": "English",
#             "originLang": "Spanish",
#         },
#         headers={
#             "Authorization": "Bearer " + access_token
#         }
#     )
#     assert response.status_code == 200
#     completion = response.json()
#     senses = parse_word_senses_completion(completion.choices[0].message.content)
#     assert senses == ['Hacer', 'Fabricar', 'Construir', 'Crear', 'Formar', 'Elaborar', 'Generar', 'Producir', 'Realizar', 'Lograr']

# @pytest.mark.asyncio
# async def test_insert_new_explanation_success(
#     client: AsyncClient, 
#     access_token: str, 
# ):
#     response = await client.post(
#         "/api/v0/explanation",
#         json={
#             word="fancypantsword",
#             studyLang
#         }
#     )