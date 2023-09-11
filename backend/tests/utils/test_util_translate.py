from app.utils.translate import generate_explanation
from app.models.translate import Explanation

def test_generate_explanation_successful():
    explanation = 'explanation'
    language = 'nl_NL'
    generated_expl = generate_explanation(explanation=explanation, language=language)
    expected_expl = Explanation(
        nl_NL=explanation,
        es_US="",
        en_US=""
    )
    assert generated_expl == expected_expl