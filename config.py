import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el .env
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
