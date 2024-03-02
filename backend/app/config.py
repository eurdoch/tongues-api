from decouple import config
from pydantic import BaseModel

class Settings(BaseModel):
    """Server config settings"""

    testing = config("TESTING", default=False, cast=bool)

    # Mongo Engine settings
    #mongo_uri = config("MONGO_URI") if not testing else config("MONGO_TEST_URI")
    #mongo_uri = config("MONGO_URI")


CONFIG = Settings()
