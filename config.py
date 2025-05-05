import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30