from beanie import Document

class Model(Document):
    name: str
    section: str
    language: str
