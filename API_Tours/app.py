from flask import Flask, jsonify, request
from functools import wraps
from config import Config, get_api_key
from db import init_mysql, mysql

app = Flask(__name__)

init_mysql(app, Config)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == get_api_key():
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Acceso no autorizado: API Key inválida o no proporcionada"}), 401
    return decorated_function


@app.route('/tours', methods=['GET'])
def get_all_tours():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tours")
    tours = cur.fetchall()
    cur.close()
    return jsonify(tours)

@app.route('/tours/<int:id>', methods=['GET'])
def get_tour_by_id(id):
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tours WHERE id = %s", (id,))
    tour = cur.fetchone()
    cur.close()
    if tour:
        return jsonify(tour)
    return jsonify({"error": "Tour no encontrado"}), 404

@app.route('/tours', methods=['POST'])
@require_api_key
def create_tour():
    data = request.get_json()
    nombre = data['nombre']
    destino = data['destino']
    descripcion = data['descripcion']
    duracion_horas = data['duracion_horas']
    precio = data['precio']
    cupos_disponibles = data['cupos_disponibles']
    guia_id = data.get('guia_id')

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO tours (nombre, destino, descripcion, duracion_horas, precio, cupos_disponibles, guia_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (nombre, destino, descripcion, duracion_horas, precio, cupos_disponibles, guia_id)
    )
    mysql.connection.commit()
    cur.close()
    return jsonify({"mensaje": "Tour creado exitosamente"}), 201

@app.route('/tours/<int:id>', methods=['PUT'])
@require_api_key
def update_tour(id):
    data = request.get_json()
    nombre = data['nombre']
    destino = data['destino']
    descripcion = data['descripcion']
    duracion_horas = data['duracion_horas']
    precio = data['precio']
    cupos_disponibles = data['cupos_disponibles']
    guia_id = data.get('guia_id')

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tours
        SET nombre = %s,
            destino = %s,
            descripcion = %s,
            duracion_horas = %s,
            precio = %s,
            cupos_disponibles = %s,
            guia_id = %s
        WHERE id = %s
    """, (nombre, destino, descripcion, duracion_horas, precio, cupos_disponibles, guia_id, id))
    mysql.connection.commit()
    cur.close()
    
    if cur.rowcount == 0:
        return jsonify({"error": "Tour no encontrado"}), 404
        
    return jsonify({"mensaje": "Tour actualizado exitosamente"})

@app.route('/tours/<int:id>', methods=['DELETE'])
@require_api_key
def delete_tour(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tours WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Tour no encontrado para eliminar"}), 404

    return jsonify({"mensaje": "Tour eliminado exitosamente"})

@app.route('/tours/<int:id>/cupos', methods=['PATCH'])
@require_api_key
def update_tour_cupos(id):

    data = request.get_json()
    if 'cantidad' not in data or 'accion' not in data:
        return jsonify({"error": "Faltan los campos 'cantidad' y 'accion'"}), 400

    cantidad = data['cantidad']
    accion = data['accion']

    cur = mysql.connection.cursor()
    cur.execute("SELECT cupos_disponibles FROM tours WHERE id = %s", (id,))
    tour = cur.fetchone()

    if not tour:
        cur.close()
        return jsonify({"error": "Tour no encontrado"}), 404

    cupos_actuales = tour['cupos_disponibles']

    if accion == 'decrementar':
        if cupos_actuales >= cantidad:
            nuevos_cupos = cupos_actuales - cantidad
        else:
            cur.close()
            return jsonify({"error": "No hay suficientes cupos disponibles"}), 409
    elif accion == 'incrementar':
        nuevos_cupos = cupos_actuales + cantidad
    else:
        cur.close()
        return jsonify({"error": "Acción no válida. Use 'decrementar' o 'incrementar'"}), 400

    cur.execute("UPDATE tours SET cupos_disponibles = %s WHERE id = %s", (nuevos_cupos, id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"mensaje": f"Cupos actualizados. Nuevo total: {nuevos_cupos}"})


@app.route('/guias', methods=['GET'])
def get_all_guias():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, email, biografia FROM guias")
    guias = cur.fetchall()
    cur.close()
    return jsonify(guias)

@app.route('/guias', methods=['POST'])
@require_api_key
def create_guia():
    data = request.get_json()
    nombre = data['nombre']
    email = data['email']
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO guias (nombre, email) VALUES (%s, %s)", (nombre, email))
    mysql.connection.commit()
    cur.close()
    return jsonify({"mensaje": "Guía creado exitosamente"}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5001)