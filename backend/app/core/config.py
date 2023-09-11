import os

from dotenv import load_dotenv

load_dotenv(".env")

TESTING = True if os.getenv('TESTING') == "1" else False
# MONGODB_URL = "mongodb://localhost:27017" if TESTING else os.getenv('MONGO_URL')
MONGODB_URL = "mongodb://localhost:27017"