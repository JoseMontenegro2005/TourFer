import psycopg2
import psycopg2.extras

def get_db_connection(config):
        conn = psycopg2.connect(
            host=config.PG_HOST,
            database=config.PG_DB,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            port=config.PG_PORT
        )
        return conn