from app.models.translate import Explanation

def generate_explanation(explanation: str, language: str):
    expl_dict = {}
    for field in Explanation.__fields__:
        expl_dict[field] = explanation if field == language else ""
    return Explanation.parse_obj(expl_dict)