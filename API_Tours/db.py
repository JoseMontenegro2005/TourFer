from flask_mysqldb import MySQL

mysql = MySQL()

def init_mysql(app, cfg):
    """
    Inicializa la extensión MySQL con la configuración de la app.
    """
    app.config['MYSQL_HOST'] = cfg.MYSQL_HOST
    app.config['MYSQL_USER'] = cfg.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = cfg.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = cfg.MYSQL_DB
    app.config['MYSQL_CURSORCLASS'] = cfg.MYSQL_CURSORCLASS
    
    mysql.init_app(app)
    return mysql