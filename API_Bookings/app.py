from flask import Flask, jsonify, request
import requests
from config import Config, get_catalogo_api_config
from db import init_mysql, mysql
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
init_mysql(app, Config)
catalogo_api_config = get_catalogo_api_config()
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- NUEVO DECORADOR DE ADMINISTRADOR ---
# Este decorador personalizado verifica que el usuario tenga un token Y que su rol sea 1
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Obtiene todas las "claims" (datos) dentro del token
        claims = get_jwt()
        # Verificamos si la claim 'rol_id' es igual a 1 (Admin)
        if claims.get('rol_id') == 1:
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Acceso no autorizado: Se requiere rol de administrador"}), 403 # 403 Forbidden
    return wrapper

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/register', methods=['POST'])
def register():
    """
    RUTA MODIFICADA: No necesita cambios en el código.
    Gracias al 'DEFAULT 2' en la base de datos, cualquier usuario
    insertado desde aquí será automáticamente un Cliente.
    """
    data = request.get_json()
    nombre = data['nombre']
    email = data['email']
    password_plana = data['password']

    password_hash = bcrypt.generate_password_hash(password_plana).decode('utf-8')

    cur = mysql.connection.cursor()
    try:
        # El INSERT no necesita mencionar 'rol_id', la BD lo maneja.
        cur.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password_hash)
        )
        mysql.connection.commit()
    except:
        cur.close()
        return jsonify({"error": "El email ya existe"}), 409
    finally:
        cur.close()
        
    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    RUTA MODIFICADA: Ahora consultamos el 'rol_id' y lo añadimos
    al token JWT usando 'additional_claims'.
    """
    data = request.get_json()
    email = data.get('email')
    password_plana = data.get('password')

    if not email or not password_plana:
        return jsonify({"error": "Faltan email o password"}), 400

    cur = mysql.connection.cursor()
    # Pedimos el 'rol_id' además del id y password
    cur.execute("SELECT id, password, rol_id FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()

    if usuario and bcrypt.check_password_hash(usuario['password'], password_plana):
        # Creamos un diccionario con las "claims" adicionales
        additional_claims = {"rol_id": usuario['rol_id']}
        
        # Generamos el token
        access_token = create_access_token(
            identity=str(usuario['id']),
            additional_claims=additional_claims
        )
        return jsonify(access_token=access_token)
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

# --- NUEVA RUTA DE ADMINISTRADOR ---
@app.route('/admin/usuarios', methods=['GET'])
@admin_required # <-- ¡Protegida con nuestro nuevo decorador!
def get_all_users():
    """
    NUEVA RUTA: Solo los usuarios con rol_id=1 pueden acceder.
    Devuelve una lista de todos los usuarios en el sistema.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, email, rol_id FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return jsonify(usuarios)

# --- RUTAS DE RESERVAS (Sin cambios en el código, pero ahora más seguras) ---
# ... (El resto de tus rutas: /reservas, /mis-reservas, etc.) ...
# ... (No necesitan cambios porque @jwt_required() sigue funcionando igual) ...

@app.route('/reservas', methods=['POST'])
@jwt_required() 
def create_reserva():
    # (Este código es el mismo de antes)
    current_user_id = get_jwt_identity()
    data = request.get_json()
    tour_id = data['tour_id']
    cantidad_personas = data['cantidad_personas']
    
    # ... (resto de la lógica de crear reserva) ...
    # ... (La comunicación con la catalogo_api sigue igual) ...
    
    # --- PASO 1: Consultar la API de Catálogo (Esto no cambia) ---
    try:
        tour_url = f"{catalogo_api_config['url']}/tours/{tour_id}"
        response = requests.get(tour_url)
        if response.status_code != 200:
            return jsonify({"error": "El tour solicitado no existe"}), 404
        tour_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

    # --- PASO 2: Validar cupos (Esto no cambia) ---
    if tour_data['cupos_disponibles'] < cantidad_personas:
        return jsonify({
            "error": "No hay suficientes cupos disponibles",
            "cupos_disponibles": tour_data['cupos_disponibles']
        }), 409

    # --- PASO 3: Guardar reserva (Modificado para usar el ID del token) ---
    costo_total = float(tour_data['precio']) * cantidad_personas
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO reservas (tour_id, usuario_id, cantidad_personas, costo_total, estado) VALUES (%s, %s, %s, %s, %s)",
        (tour_id, current_user_id, cantidad_personas, costo_total, 'Confirmada') # Usamos current_user_id
    )
    mysql.connection.commit()
    reserva_id = cur.lastrowid
    cur.close()

    # --- PASO 4: Descontar cupos (Esto no cambia, AÚN USA LA X-API-KEY) ---
    try:
        update_cupos_url = f"{catalogo_api_config['url']}/tours/{tour_id}/cupos"
        headers = {'X-API-Key': catalogo_api_config['key']} # <-- ¡La API Key M2M sigue aquí!
        payload = {'accion': 'decrementar', 'cantidad': cantidad_personas}
        
        requests.patch(update_cupos_url, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"ADVERTENCIA: Reserva {reserva_id} creada, pero falló la actualización de cupos: {e}")

    return jsonify({
        "mensaje": "Reserva creada exitosamente",
        "reserva_id": reserva_id,
        "costo_total": costo_total
    }), 201
    
@app.route('/mis-reservas', methods=['GET'])
@jwt_required()
def get_mis_reservas():
    # (Este código es el mismo de antes)
    current_user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reservas WHERE usuario_id = %s", (current_user_id,))
    reservas = cur.fetchall()
    cur.close()
    return jsonify(reservas)

# --- Arranque de la Aplicación (Sin cambios) ---
if __name__ == '__main__':
    app.run(debug=True, port=5002)