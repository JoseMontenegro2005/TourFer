from flask_mysqldb import MySQL

mysql = MySQL()

def init_mysql(app, cfg):

    app.config['MYSQL_HOST'] = cfg.MYSQL_HOST
    app.config['MYSQL_USER'] = cfg.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = cfg.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = cfg.MYSQL_DB
    app.config['MYSQL_PORT'] = cfg.MYSQL_PORT
    app.config['MYSQL_CURSORCLASS'] = cfg.MYSQL_CURSORCLASS

    if cfg.MYSQL_SSL_CA and os.path.exists(cfg.MYSQL_SSL_CA):
        app.config['MYSQL_SSL_CA'] = cfg.MYSQL_SSL_CA
    else:
        print("ADVERTENCIA: No se encontró ca.pem, la conexión a Aiven podría fallar.")
        
    mysql.init_app(app)
    return mysql
