import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PG_HOST = os.getenv("PG_HOST")
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_DB = "postgres" # Supabase usa esta por defecto
    PG_PORT = 5432

    API_KEY = os.getenv("API_KEY", "tourfer-catalogo-secret-key")
# ...
    MYSQL_SSL_DISABLED = False
    
    MYSQL_SSL = {'ssl': {'ca': '/etc/ssl/cert.pem'}} 
def get_api_key():
    return Config.API_KEY