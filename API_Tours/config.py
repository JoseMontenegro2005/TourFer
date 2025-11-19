import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306)) 
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_CURSORCLASS = "DictCursor"

    API_KEY = os.getenv("API_KEY", "tourfer-catalogo-secret-key")
# ...
    MYSQL_SSL_DISABLED = False
    
    MYSQL_SSL = {'ssl': {'ca': '/etc/ssl/cert.pem'}} 
def get_api_key():
    return Config.API_KEY