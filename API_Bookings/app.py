from flask import Flask, jsonify, request
import requests
from config import Config, get_catalogo_api_config
from db import init_mysql, mysql
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
init_mysql(app, Config)
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

    cur = mysql.connection.cursor()
    try:
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
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Faltan email o password"}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password, rol_id FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()

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
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, email, rol_id FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return jsonify(usuarios)


@app.route('/reservas', methods=['POST'])
@jwt_required() 
def create_reserva():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    tour_id = data['tour_id']
    cantidad_personas = data['cantidad_personas']

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
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO reservas (tour_id, usuario_id, cantidad_personas, costo_total, estado) VALUES (%s, %s, %s, %s, %s)",
        (tour_id, current_user_id, cantidad_personas, costo_total, 'Confirmada') 
    )
    mysql.connection.commit()
    reserva_id = cur.lastrowid
    cur.close()

    try:
        update_cupos_url = f"{catalogo_api_config['url']}/tours/{tour_id}/cupos"
        headers = {'X-API-Key': catalogo_api_config['key']}
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
    current_user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reservas WHERE usuario_id = %s", (current_user_id,))
    reservas = cur.fetchall()
    cur.close()
    return jsonify(reservas)

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
    """Proxy público para ver todos los tours."""
    url = f"{catalogo_api_config['url']}/tours"
    try:
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/public/tours/<int:id>', methods=['GET'])
def public_get_tour_by_id(id):
    """Proxy público para ver un tour."""
    url = f"{catalogo_api_config['url']}/tours/{id}"
    try:
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503

@app.route('/public/guias', methods=['GET'])
def public_get_all_guias():
    """Proxy público para ver todos los guías."""
    url = f"{catalogo_api_config['url']}/guias"
    try:
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al comunicar con API Catálogo: {e}"}), 503


if __name__ == '__main__':
    app.run(debug=True, port=5002)