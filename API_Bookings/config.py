import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PG_HOST = os.getenv("PG_HOST")
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_DB = "postgres" # Supabase usa esta por defecto
    PG_PORT = 5432 
    CATALOGO_API_URL = os.getenv("CATALOGO_API_URL", "http://127.0.0.1:5001")

    CATALOGO_API_KEY = os.getenv("CATALOGO_API_KEY", "tourfer-catalogo-secret-key")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tourfer12345")

def get_catalogo_api_config():
    return {
        "url": Config.CATALOGO_API_URL,
        "key": Config.CATALOGO_API_KEY
    }