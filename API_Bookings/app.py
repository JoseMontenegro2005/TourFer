from flask import Flask, jsonify, request
import requests
from config import Config, get_catalogo_api_config
# Importamos tu función de conexión desde db.py
from db import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Configuración de API externa
catalogo_api_config = get_catalogo_api_config()
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('rol_id') == 1:
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Acceso no autorizado: Se requiere rol de administrador"}), 403 
    return wrapper

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nombre = data['nombre']
    email = data['email']
    password = data['password']

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Conexión usando tu función importada de db.py
    conn = get_db_connection(Config)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password_hash)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
    except psycopg2.IntegrityError:
        # Captura error de duplicados (email único)
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "El email ya existe"}), 409
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Faltan email o password"}), 400

    conn = get_db_connection(Config)
    # RealDictCursor permite acceder a las columnas por nombre (usuario['password'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, password, rol_id FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if usuario and bcrypt.check_password_hash(usuario['password'], password):
        rol = {"rol_id": usuario['rol_id']}
        
        access_token = create_access_token(
            identity=str(usuario['id']),
            additional_claims=rol
        )
        return jsonify(access_token=access_token)
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/admin/usuarios', methods=['GET'])
@admin_required
def get_all_users():
    conn = get_db_connection(Config)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nombre, email, rol_id FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(usuarios)


@app.route('/reservas', methods=['POST'])
@jwt_required() 
def create_reserva():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    tour_id = data['tour_id']
    cantidad_personas = data['cantidad_personas']
    fecha = data.get('fecha', 'Fecha sin definir')
    try:
        tour_url = f"{catalogo_api_config['url']}/tours/{tour_id}"
        response = requests.get(tour_url)
        if response.status_code != 200:
            return jsonify({"error": "El tour solicitado no existe"}), 404
        tour_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

    if tour_data['cupos_disponibles'] < cantidad_personas:
        return jsonify({
            "error": "No hay suficientes cupos disponibles",
            "cupos_disponibles": tour_data['cupos_disponibles']
        }), 409

    costo_total = float(tour_data['precio']) * cantidad_personas
    
    conn = get_db_connection(Config)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    user_email = "sin_correo@tourfer.com"
    try:
        # NOTA IMPORTANTE: PostgreSQL no tiene lastrowid. 
        # Usamos RETURNING id para obtener el ID generado.
        cur.execute(
            """
            INSERT INTO reservas (tour_id, usuario_id, cantidad_personas, costo_total, estado) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
            """,
            (tour_id, current_user_id, cantidad_personas, costo_total, 'Confirmada') 
        )
        nuevo_registro = cur.fetchone()
        reserva_id = nuevo_registro['id']

        cur.execute("SELECT email FROM usuarios WHERE id = %s", (current_user_id,))
        usuario_data = cur.fetchone()
        if usuario_data:
            user_email = usuario_data['email']

        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": f"Error guardando reserva: {str(e)}"}), 500
    
    cur.close()
    conn.close()

    # 4. Actualizar cupos en API externa
    try:
        update_cupos_url = f"{catalogo_api_config['url']}/tours/{tour_id}/cupos"
        headers = {'X-API-Key': catalogo_api_config['key']}
        payload = {'accion': 'decrementar', 'cantidad': cantidad_personas}
        
        requests.patch(update_cupos_url, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"ADVERTENCIA: Reserva {reserva_id} creada, pero falló la actualización de cupos: {e}")
    try:
        notificaciones_url = 'http://tourfer-notificaciones.onrender.com/enviar-correo' 
        
        headers = {
            'Content-Type': 'application/json',
            'X-Notification-Key': 'clave_segura_local_123' 
                            }
        requests.post(notificaciones_url, json={
            "email": user_email,
            "mensaje": f"¡Hola! Tu reserva #{reserva_id} para el {fecha} ha sido confirmada."
        }, headers=headers, timeout=2)
        
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo enviar la notificación: {e}")

    return jsonify({
        "mensaje": "Reserva creada exitosamente",
        "reserva_id": reserva_id,
        "costo_total": costo_total
    }), 201

    
    
@app.route('/mis-reservas', methods=['GET'])
@jwt_required()
def get_mis_reservas():
    current_user_id = get_jwt_identity()
    conn = get_db_connection(Config)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM reservas WHERE usuario_id = %s", (current_user_id,))
    reservas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(reservas)

# --- RUTAS DE PROXY ADMIN (Sin cambios de lógica de BD, solo requests) ---

@app.route('/admin/tours', methods=['POST'])
@admin_required
def admin_create_tour():
    data = request.get_json()
    url = f"{catalogo_api_config['url']}/tours"
    headers = {'X-API-Key': catalogo_api_config['key']}
    try:
        response = requests.post(url, json=data, headers=headers)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/admin/tours/<int:id>', methods=['PUT'])
@admin_required
def admin_update_tour(id):
    data = request.get_json()
    url = f"{catalogo_api_config['url']}/tours/{id}"
    headers = {'X-API-Key': catalogo_api_config['key']}
    try:
        response = requests.put(url, json=data, headers=headers)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/admin/tours/<int:id>', methods=['DELETE'])
@admin_required
def admin_delete_tour(id):
    url = f"{catalogo_api_config['url']}/tours/{id}"
    headers = {'X-API-Key': catalogo_api_config['key']}
    try:
        response = requests.delete(url, headers=headers)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503
    
@app.route('/admin/guias', methods=['POST'])
@admin_required
def admin_create_guia():
    data = request.get_json()
    url = f"{catalogo_api_config['url']}/guias"
    headers = {'X-API-Key': catalogo_api_config['key']} 
    try:
        response = requests.post(url, json=data, headers=headers)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/public/tours', methods=['GET'])
def public_get_all_tours():
    url = f"{catalogo_api_config['url']}/tours"
    try:
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/public/tours/<int:id>', methods=['GET'])
def public_get_tour_by_id(id):
    url = f"{catalogo_api_config['url']}/tours/{id}"
    try:
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/public/guias', methods=['GET'])
def public_get_all_guias():
    url = f"{catalogo_api_config['url']}/guias"
    try:
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

if __name__ == '__main__':
    app.run(debug=True, port=5002)