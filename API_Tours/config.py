import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuración para la API de Catálogo.
    """
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "user_catalogo")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "tourpass123")
    MYSQL_DB = os.getenv("MYSQL_DB", "catalogo_db")
    MYSQL_CURSORCLASS = "DictCursor"

    API_KEY = os.getenv("API_KEY", "tourfer-catalogo-secret-key")

def get_api_key():
    """Función para obtener la clave de API desde la configuración."""
    return Config.API_KEY