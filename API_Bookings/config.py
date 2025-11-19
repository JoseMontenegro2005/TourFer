import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 24021))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB") 
    MYSQL_CURSORCLASS = "DictCursor"
    
    MYSQL_SSL_DISABLED = False
    MYSQL_SSL = {'ssl': {'ca': '/etc/ssl/cert.pem'}} 
    CATALOGO_API_URL = os.getenv("CATALOGO_API_URL", "http://127.0.0.1:5001")

    CATALOGO_API_KEY = os.getenv("CATALOGO_API_KEY", "tourfer-catalogo-secret-key")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tourfer12345")

def get_catalogo_api_config():
    return {
        "url": Config.CATALOGO_API_URL,
        "key": Config.CATALOGO_API_KEY
    }